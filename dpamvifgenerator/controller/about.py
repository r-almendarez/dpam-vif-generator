from PySide6.QtWidgets import QDialog

from dpamvifgenerator import buildinfo
from dpamvifgenerator.utility import get_data_file_path, load_ui_file


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.ui = load_ui_file(get_data_file_path("uifiles", "about.ui"))
        # Connect Signals and Slots
        self.connect_signals_and_slots()
        # Initialize UI
        self.initialize_ui()

    def show(self):
        self.ui.show()

    def quit(self):
        self.ui.close()

    def connect_signals_and_slots(self):
        # Connect button box options
        self.ui.button_box.accepted.connect(self.accept)

    def initialize_ui(self):
        # Set versions info
        self.ui.dpam_vif_generator_version.setText(buildinfo.__version__)
        self.ui.dpam_vif_spec_version.setText(buildinfo.__dpam_vif_spec_version__)
        self.ui.usbif_vif_spec_version.setText(buildinfo.__usbif_vif_spec_version__)
