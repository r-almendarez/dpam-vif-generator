import logging
import os
from xml.etree import ElementTree as ET

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QCheckBox, QComboBox, QFileDialog, QMainWindow

from dpamvifgenerator import script
from dpamvifgenerator.utility import XML_INDENT, get_data_file_path, load_ui_file


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
        value = self.ds.get(name, "")
        logging.debug("Retrieved {} with value {}".format(name, value))
        return value

    def generate_settings(self):
        # Get default DP XML
        default_xml_string = """<?xml version="1.0" ?>
<vif:VIF xmlns:opt="http://usb.org/VendorInfoFileOptionalContent.xsd" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:vif="http://usb.org/VendorInfoFile.xsd">
    <vif:Component>
        <vif:Port_Label>0</vif:Port_Label>
        <vif:SOPSVID>
            <vif:SVID_SOP value="65281">FF01</vif:SVID_SOP>
            <vif:SVID_Modes_Fixed_SOP value="true"/>
            <vif:SVID_Num_Modes_Min_SOP value="1"/>
            <vif:SVID_Num_Modes_Max_SOP value="1"/>
            <vif:SOPSVIDModeList>
                <vif:SOPSVIDMode>
                    <vif:SVID_Mode_Enter_SOP value="true"/>
                    <vif:SVID_Mode_Recog_Value_SOP value="786501">0x000C0045</vif:SVID_Mode_Recog_Value_SOP>
                </vif:SOPSVIDMode>
            </vif:SOPSVIDModeList>
        </vif:SOPSVID>
    </vif:Component>
    <vif:Component>
        <vif:Port_Label>1</vif:Port_Label>
        <vif:SOPSVID>
            <vif:SVID_SOP value="65281">FF01</vif:SVID_SOP>
            <vif:SVID_Modes_Fixed_SOP value="true"/>
            <vif:SVID_Num_Modes_Min_SOP value="1"/>
            <vif:SVID_Num_Modes_Max_SOP value="1"/>
            <vif:SOPSVIDModeList>
                <vif:SOPSVIDMode>
                    <vif:SVID_Mode_Enter_SOP value="true"/>
                    <vif:SVID_Mode_Recog_Value_SOP value="786501">0x000C0045</vif:SVID_Mode_Recog_Value_SOP>
                </vif:SOPSVIDMode>
            </vif:SOPSVIDModeList>
        </vif:SOPSVID>
    </vif:Component>
</vif:VIF>
        """  # noqa: E501
        settings_tree = ET.ElementTree(ET.fromstring(default_xml_string))
        ET.indent(settings_tree, space=XML_INDENT, level=0)
        # Update based on user provided arguments
        pass
        # Write to local file
        settings = os.path.join(self.user_data_dir, "settings.xml")
        settings_tree.write(settings, encoding="utf8", method="xml")
        # Return settings file path
        return settings
