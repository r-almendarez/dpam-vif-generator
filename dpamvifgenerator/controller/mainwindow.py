import os

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QFileDialog, QMainWindow

from dpamvifgenerator import script
from dpamvifgenerator.utility import get_data_file_path, load_ui_file


class MainWindow(QMainWindow):
    application_is_closing = Signal()

    def __init__(self, ds, splash_message=lambda x: None):
        super().__init__()
        self.ds = ds
        self.ui = load_ui_file(get_data_file_path("uifiles", "mainwindow.ui"))

        # Populate UI

        # Connect Signals and Slots
        self.connect_signals_and_slots()

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
        filename = os.path.abspath(filename)
        self.ui.input_line_edit.setText(filename)

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
        settings = script.DPAMVIFGenerator.generate_settings()

        import pdb

        pdb.set_trace()

        # Generate output VIF XML file
        script.main(
            **{
                "in_vif": self.ui.input_line_edit.text(),
                "out_vif": filename,
                "settings": settings,
            }
        )

    def save_to_store(self, name: str, value):
        self.ds[name] = value

    def get_from_store(self, name: str):
        return self.ds.get(name, "")
