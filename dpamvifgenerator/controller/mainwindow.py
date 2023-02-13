from PySide6.QtCore import Signal
from PySide6.QtWidgets import QMainWindow

from dpamvifgenerator.utility import get_data_file_path, load_ui_file


class MainWindow(QMainWindow):
    application_is_closing = Signal()

    def __init__(self, splash_message=lambda x: None):
        super().__init__()
        self.ui = load_ui_file(get_data_file_path("uifiles", "mainwindow.ui"))

        # Populate UI
        # Connect Signals and Slots

    def show(self):
        self.ui.show()

    def app_quitting(self):
        self.quit()

    def quit(self):
        self.application_is_closing.emit()
        self.ui.close()
