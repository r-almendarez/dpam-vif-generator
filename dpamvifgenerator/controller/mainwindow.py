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
from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QGroupBox,
    QMainWindow,
    QWidget,
)

from dpamvifgenerator import buildinfo, script
from dpamvifgenerator.utility import XML_INDENT, get_data_file_path, load_ui_file

# Globals
UI_TAB_SUFFIX = "_tab"
UI_CBB_SUFFIX = "_cbb"
UI_CHECKBOX_SUFFIX = "_checkbox"
UI_GROUPBOX_SUFFIX = "_groupbox"


class MainWindow(QMainWindow):
    application_is_closing = Signal()

    def __init__(self, ds, user_data_dir, splash_message=lambda x: None):
        super().__init__()
        self.ds = ds
        self.user_data_dir = user_data_dir
        self.ui = load_ui_file(get_data_file_path("uifiles", "mainwindow.ui"))
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

        # Setup thread to generate VIF
        pass

        # Generate DPAM Settings XML file
        settings = self.generate_settings()

        # Generate output VIF XML file
        script.main(
            **{
                "in_vif": self.ui.input_line_edit.text(),
                "out_vif": filename,
                "settings": settings,
            }
        )

        # Clean up settings file
        os.remove(settings)

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
        element_name = "opt:{}".format(field_name.removesuffix(UI_CBB_SUFFIX))
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
        element_name = "opt:{}".format(field_name.removesuffix(UI_CHECKBOX_SUFFIX))
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
                text_list.append(checkbox_name.removesuffix(UI_CHECKBOX_SUFFIX))
        # Build element
        element_name = "opt:{}".format(field_name.removesuffix(UI_GROUPBOX_SUFFIX))
        element = ET.Element(element_name, value=str(group_value))
        element.text = ", ".join(text_list)
        # Return built element
        return element
