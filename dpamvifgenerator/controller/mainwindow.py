######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import logging
import os
import shutil
from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QMainWindow,
    QProgressBar,
    QWidget,
)

from dpamvifgenerator import buildinfo, script
from dpamvifgenerator.controller.about import AboutDialog
from dpamvifgenerator.utility import XML_INDENT, get_data_file_path, load_ui_file
from dpamvifgenerator.utility.worker import Worker

# Globals
UI_TAB_SUFFIX = "_tab"
UI_CBB_SUFFIX = "_cbb"
UI_CHECKBOX_SUFFIX = "_checkbox"
UI_GROUPBOX_SUFFIX = "_groupbox"
UI_SUFFIXES = [UI_TAB_SUFFIX, UI_CBB_SUFFIX, UI_CHECKBOX_SUFFIX, UI_GROUPBOX_SUFFIX]


class MainWindow(QMainWindow):
    application_is_closing = Signal()

    def __init__(self, ds, user_data_dir, splash_message=lambda x: None):
        super().__init__()
        self.setWindowTitle(buildinfo.__product__)
        self.ds = ds
        self.user_data_dir = user_data_dir
        self.ui = load_ui_file(get_data_file_path("uifiles", "mainwindow.ui"))
        self.worker = None
        self.action_thread = None
        # Connect Signals and Slots
        self.connect_signals_and_slots()
        # Initialize UI
        self.initialize_ui()

    def show(self):
        self.ui.show()

    def app_quitting(self):
        self.quit()

    def quit(self):
        self.application_is_closing.emit()
        self.ui.close()

    def connect_signals_and_slots(self):
        # Connect menubar options
        self.ui.action_quit.triggered.connect(self.quit)
        self.ui.action_export_settings.triggered.connect(self.export_settings)
        self.ui.action_import_settings.triggered.connect(self.import_settings)
        self.ui.action_about.triggered.connect(self.show_about)

        # Connect buttons
        self.ui.browse_input_button.clicked.connect(self.browse_input_button)
        self.ui.save_as_button.clicked.connect(self.save_as_output)

        # Connect line edits
        self.ui.input_line_edit.textChanged.connect(
            lambda x: self.save_to_store("user_path_to_input", x)
        )

        # Connect port label
        self.ui.port_label_cbb.currentIndexChanged.connect(
            lambda x: self.port_label_changed(x)
        )

        # Connect port widgets
        def port_widget_changed(widget_name: str, value):
            port_label = self.ui.port_label_cbb.currentIndex()
            store_label = "{}_{}".format(widget_name, port_label)
            self.save_to_store(store_label, value)

        # Connect comboboxes
        for cbb in self.ui.sop_displayport_capabilities_tab.findChildren(
            QComboBox
        ) + self.ui.sopp_displayport_capabilities_tab.findChildren(QComboBox):
            cbb.currentIndexChanged.connect(
                lambda x, cbb_name=cbb.objectName(): port_widget_changed(cbb_name, x)
            )

        # Connect checkboxes
        for checkbox in self.ui.sop_displayport_capabilities_tab.findChildren(
            QCheckBox
        ):
            checkbox.stateChanged.connect(
                lambda x, checkbox_name=checkbox.objectName(): port_widget_changed(
                    checkbox_name, x
                )
            )

    def initialize_ui(self):
        # Disable UI by default until an input VIF is loaded
        self.ui.port_label_cbb.setEnabled(False)
        self.ui.sop_displayport_capabilities_tab.setEnabled(False)
        self.ui.sopp_displayport_capabilities_tab.setEnabled(False)

        # Setup UI defaults
        ds_input_vif = self.get_from_store("user_path_to_input")
        if ds_input_vif:
            self.populate_from_input_vif(ds_input_vif)

    def port_label_changed(self, port_value):
        # Attempt to load port data from store
        def get_port_widget_data(widget_name: str):
            store_label = "{}_{}".format(widget_name, port_value)
            return self.get_from_store(store_label)

        for cbb in self.ui.sop_displayport_capabilities_tab.findChildren(
            QComboBox
        ) + self.ui.sopp_displayport_capabilities_tab.findChildren(QComboBox):
            cbb_index = get_port_widget_data(cbb.objectName())
            if cbb_index:
                cbb.setCurrentIndex(cbb_index)
            else:
                cbb.setCurrentIndex(0)

        for checkbox in self.ui.sop_displayport_capabilities_tab.findChildren(
            QCheckBox
        ):
            checkbox_state = get_port_widget_data(checkbox.objectName())
            if checkbox_state:
                checkbox.setCheckState(Qt.CheckState(checkbox_state))
            else:
                checkbox.setCheckState(Qt.CheckState.Unchecked)

    def browse_input_button(self):
        # Get user input filename
        filename = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select .xml File",
            dir=self.ui.input_line_edit.text(),
            filter="XML Files (*.xml)",
        )[0]
        # Return if no file was selected
        if filename == "":
            return
        # User selected a file
        self.populate_from_input_vif(filename)

    def populate_from_input_vif(self, input_vif_filename):
        filename = os.path.abspath(input_vif_filename)
        self.ui.input_line_edit.setText(filename)
        # Attempt to load file as VIF. File may no longer exist
        try:
            input_vif = script.DPAMVIFGenerator.load_input_vif(filename)
        except script.InvalidInputVIF:
            # Just return to allow user to try again
            return
        # Populate ports list
        self.ui.port_label_cbb.clear()
        prefix_map = {"vif": "http://usb.org/VendorInfoFile.xsd"}
        for port in input_vif.getroot().findall(".//vif:Component", prefix_map):
            self.ui.port_label_cbb.addItem(port.find("vif:Port_Label", prefix_map).text)
        # Activate UI elements
        self.ui.port_label_cbb.setEnabled(True)
        self.ui.sop_displayport_capabilities_tab.setEnabled(True)
        self.ui.sopp_displayport_capabilities_tab.setEnabled(True)

    def save_as_output(self):
        # Get user output filename
        filename = QFileDialog.getSaveFileName(
            parent=self,
            caption="Save As",
            dir=self.get_from_store("user_path_to_output"),
            filter="USBIF VIF XML File (*.xml)",
        )[0]
        # Return if no file name was provided
        if filename == "":
            return

        # Store filename in datastore
        filename = os.path.abspath(filename)
        self.save_to_store("user_path_to_output", filename)

        # Define action thread
        def generate_output_vif_xml(progress: QProgressBar):
            try:
                # Set status text and progress
                progress.setValue(0)
                self.ui.save_status_label.setText(
                    """<p>
                        <span style=" font-weight:700;">
                            Status
                        </span>: Generating DPAM VIF Settings
                    </p>"""
                )

                # Generate DPAM Settings XML file
                settings = self.generate_settings()
                progress.setValue(100)

                # Generate output VIF XML file
                self.ui.save_status_label.setText(
                    """<p>
                        <span style=" font-weight:700;">
                            Status
                        </span>: Generating DPAM VIF XML
                    </p>"""
                )
                script.main(
                    **{
                        "in_vif": self.ui.input_line_edit.text(),
                        "out_vif": filename,
                        "settings": settings,
                        "progress": progress.setValue,
                    }
                )

                # Clean up settings file
                os.remove(settings)
            except Exception as e:
                # Block thread finished since generation errored
                self.action_thread.blockSignals(True)
                logging.error("Error: Generation Failed. {}".format(e))
                self.ui.save_status_label.setText(
                    """<p>
                        <span style=" font-weight:700;">
                            Error
                        </span>: Generation Failed. {}
                    </p>""".format(
                        e
                    )
                )

        def generation_complete():
            # Set status text
            self.ui.save_status_label.setText(
                """<p>
                    <span style=" font-weight:700;">
                        Status
                    </span>: Generation Complete
                </p>"""
            )

        # Setup thread to generate VIF
        self.worker = Worker()
        self.action_thread = QThread()
        self.worker.moveToThread(self.action_thread)
        # Connect worker signals and slots
        self.worker.action.connect(generate_output_vif_xml)
        self.worker.finished.connect(self.action_thread.quit)
        # Connect thread signals and slots
        self.action_thread.started.connect(
            lambda: self.worker.run(self.ui.save_progress_bar)
        )
        self.action_thread.finished.connect(generation_complete)
        # Start thread
        self.action_thread.start()

    def save_to_store(self, name: str, value):
        self.ds[name] = value
        logging.debug("Stored {} with value {}".format(name, value))

    def get_from_store(self, name: str):
        try:
            value = self.ds.get(name, "")
        except Exception:
            value = ""
        logging.debug("Retrieved {} with value {}".format(name, value))
        return value

    def generate_settings(self):
        # Get default DP XML
        default_xml_string = """<?xml version="1.0" encoding="utf-8"?>
<vif:VIF xmlns:vif="http://usb.org/VendorInfoFile.xsd">
  <vif:VIF_Specification>{vif_spec}</vif:VIF_Specification>
  <vif:VIF_App>
    <vif:Vendor>{vif_vendor}</vif:Vendor>
    <vif:Name>{vif_name}</vif:Name>
    <vif:Version>{vif_version}</vif:Version>
  </vif:VIF_App>
</vif:VIF>
        """.format(
            vif_spec="3.25",
            vif_vendor=str(buildinfo.__company__),
            vif_name=str(buildinfo.__product__),
            vif_version=str(buildinfo.__version__),
        )  # noqa: E501

        # Create ElementTree from xml string
        settings_tree = ET.ElementTree(ET.fromstring(default_xml_string))
        vif_root = settings_tree.getroot()
        # Register namespaces and add to root
        prefix_map = script.DPAMVIFGenerator.get_prefix_map()
        for name, namespace in prefix_map.items():
            ET.register_namespace(name, namespace)
            if name != "vif":  # xmlns:vif included in default xml string
                vif_root.attrib["xmlns:" + name] = namespace

        # Update based on user provided arguments
        ports = [
            self.ui.port_label_cbb.itemText(i)
            for i in range(self.ui.port_label_cbb.count())
        ]
        tabs = [
            self.ui.sop_displayport_capabilities_tab,
            self.ui.sopp_displayport_capabilities_tab,
        ]

        # Get current values for each port from datastore
        for port_value, port_label in enumerate(ports):
            # Add Component and Port_Label elements
            component_root = ET.Element("vif:Component")
            vif_root.append(component_root)
            port_label_element = ET.Element("vif:Port_Label")
            port_label_element.text = str(port_label)
            component_root.append(port_label_element)

            # Create optional content root
            opt_content_root = ET.Element(
                "opt:OptionalContent", identifier="DPAM", space="preserve"
            )
            component_root.append(opt_content_root)

            # Add in tab and field elements
            for tab in tabs:
                tab_root = ET.Element(
                    "opt:{}".format(
                        tab.objectName().replace(" ", "_").removesuffix(UI_TAB_SUFFIX)
                    )
                )
                opt_content_root.append(tab_root)
                for layout in tab.findChildren(
                    QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
                ):
                    for field in layout.findChildren(
                        QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
                    ):
                        # Generate XML elements for each field
                        element = self.generate_element(field, port_value)
                        if element is not None:
                            tab_root.append(element)

        # Write to local file
        settings = os.path.join(self.user_data_dir, "settings_new.xml")
        ET.indent(settings_tree, space=XML_INDENT, level=0)
        settings_tree.write(settings, encoding="utf8", method="xml")
        # Return settings file path
        return settings

    def generate_element(self, field, port_value: int) -> ET.Element | None:
        if isinstance(field, QComboBox):
            return self.generate_cbb_element(field, port_value)
        elif isinstance(field, QCheckBox):
            return self.generate_checkbox_element(field, port_value)
        elif isinstance(field, QGroupBox):
            return self.generate_groupbox_element(field, port_value)
        else:
            # Skip labels
            return None

    def generate_cbb_element(self, field: QComboBox, port_value: int) -> ET.Element:
        # Get field name, current index value, and text from ComboBox
        field_name = field.objectName()
        try:
            index_value = int(
                self.get_from_store("{}_{}".format(field_name, port_value))
            )
        except ValueError:
            index_value = 0
        text = field.itemText(index_value)
        # Build element
        element_name = "opt:{}".format(self.sanitize_widget_name(field_name))
        element = ET.Element(element_name, value=str(index_value))
        element.text = str(text)
        # Return built element
        return element

    def generate_checkbox_element(
        self, field: QCheckBox, port_value: int
    ) -> ET.Element:
        # Get field name and checked state
        field_name = field.objectName()
        try:
            checkbox_state = Qt.CheckState(
                self.get_from_store("{}_{}".format(field_name, port_value))
            )
        except ValueError:
            checkbox_state = Qt.CheckState.Unchecked
        # Build element
        element_name = "opt:{}".format(self.sanitize_widget_name(field_name))
        value_string = "true" if checkbox_state == Qt.CheckState.Checked else "false"
        element = ET.Element(element_name, value=value_string)
        # Return built element
        return element

    def generate_groupbox_element(
        self, field: QGroupBox, port_value: int
    ) -> ET.Element:
        # Get field name
        field_name = field.objectName()
        # Calculate the bit group value from groupbox checkbox fields
        group_value = 0x0
        text_list = []
        for index, checkbox in enumerate(field.findChildren(QCheckBox)):
            checkbox_name = checkbox.objectName()
            try:
                checkbox_state = Qt.CheckState(
                    self.get_from_store("{}_{}".format(checkbox_name, port_value))
                )
            except ValueError:
                checkbox_state = Qt.CheckState.Unchecked
            if checkbox_state == Qt.CheckState.Checked:
                group_value |= 1 << index
                text_list.append(self.sanitize_widget_name(checkbox_name))
        # Build element
        element_name = "opt:{}".format(self.sanitize_widget_name(field_name))
        element = ET.Element(element_name, value=str(group_value))
        element.text = ", ".join(text_list)
        # Return built element
        return element

    def sanitize_widget_name(self, widget_name: str) -> str:
        """Remove UI suffixes from widget name"""
        for suffix in UI_SUFFIXES:
            widget_name = widget_name.removesuffix(suffix)
        return widget_name

    def export_settings(self):
        """Export user settings to an XML file"""
        filename = QFileDialog.getSaveFileName(
            parent=self,
            caption="Select .xml File",
            dir=self.get_from_store("export_settings_file_path"),
            filter="XML Files (*.xml)",
        )[0]
        # Return if no file name was provided
        if filename == "":
            return

        # Store filename in datastore
        filename = os.path.abspath(filename)
        self.save_to_store("export_settings_file_path", filename)

        # Generate settings
        settings = self.generate_settings()

        # Move settings to filename path
        shutil.move(settings, filename)

    def import_settings(self):
        # Get user input settings XML
        filename = QFileDialog.getOpenFileName(
            parent=self,
            caption="Select .xml File",
            dir=self.get_from_store("import_settings_file_path"),
            filter="XML Files (*.xml)",
        )[0]
        # Return if no file was selected
        if filename == "":
            return

        # User selected a file
        filename = os.path.abspath(filename)
        self.save_to_store("import_settings_file_path", filename)

        # Load settings from input XML
        self.populate_settings_from_input_xml(filename)

    def populate_settings_from_input_xml(self, filename):
        # Attempt to load file as VIF. File may no longer exist
        try:
            dpam_settings = script.DPAMVIFGenerator.load_input_vif(filename)
        except script.InvalidInputVIF:
            # Just return to allow user to try again
            return

        # Get port DPAM settings from DPAM Settings XML
        prefix_map = script.DPAMVIFGenerator.get_prefix_map()
        port_settings = script.DPAMVIFGenerator.get_port_settings_from_vif(
            dpam_settings
        )

        # Apply settings for each port
        current_port = self.ui.port_label_cbb.currentIndex()
        ports = [
            self.ui.port_label_cbb.itemText(i)
            for i in range(self.ui.port_label_cbb.count())
        ]
        tabs = [
            self.ui.sop_displayport_capabilities_tab,
            self.ui.sopp_displayport_capabilities_tab,
        ]
        for port_value, port_label in enumerate(ports):
            self.ui.port_label_cbb.setCurrentIndex(port_value)
            # Skip if port does not exist in port settings
            if port_label not in port_settings:
                continue
            # Apply all fields from port settings that exist in UI
            for tab in tabs:
                tab_name = self.sanitize_widget_name(tab.objectName())
                for layout in tab.findChildren(
                    QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
                ):
                    for field in layout.findChildren(
                        QWidget, options=Qt.FindChildOption.FindDirectChildrenOnly
                    ):
                        # Grab setting from port settings for field
                        field_name = self.sanitize_widget_name(field.objectName())
                        field_setting = port_settings[port_label].find(
                            f".//opt:{tab_name}/opt:{field_name}", prefix_map
                        )
                        # Apply field setting to UI
                        self.apply_field_setting(field, field_setting)
        # Restore current port selection
        self.ui.port_label_cbb.setCurrentIndex(current_port)

    def apply_field_setting(self, field: QWidget | None, field_setting: ET.Element):
        if isinstance(field, QComboBox):
            self.apply_cbb_setting(field, field_setting)
        elif isinstance(field, QCheckBox):
            self.apply_checkbox_setting(field, field_setting)
        elif isinstance(field, QGroupBox):
            self.apply_groupbox_setting(field, field_setting)

    def apply_cbb_setting(self, field: QComboBox, field_setting: ET.Element):
        try:
            value = field_setting.attrib["value"]
            field.setCurrentIndex(int(value))
        except Exception:
            # Skip any malformed settings and keep trying to load
            return

    def apply_checkbox_setting(self, field: QCheckBox, field_setting: ET.Element):
        try:
            if field_setting.attrib["value"] == "false":
                field.setCheckState(Qt.CheckState.Unchecked)
            elif field_setting.attrib["value"] == "true":
                field.setCheckState(Qt.CheckState.Checked)
        except Exception:
            # Skip any malformed settings and keep trying to load
            return

    def apply_groupbox_setting(self, field: QGroupBox, field_setting: ET.Element):
        try:
            value = int(field_setting.attrib["value"])
            for index, checkbox in enumerate(field.findChildren(QCheckBox)):
                checkbox_value = value & (1 << index)
                if checkbox_value:
                    checkbox.setCheckState(Qt.CheckState.Checked)
                else:
                    checkbox.setCheckState(Qt.CheckState.Unchecked)
        except Exception:
            # Skip any malformed settings and keep trying to load
            return

    def show_about(self):
        about_dialog = AboutDialog(self)
        about_dialog.show()
