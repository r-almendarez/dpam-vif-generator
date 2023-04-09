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
import platform
import shelve

import qdarktheme
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from dpamvifgenerator import LOG_LEVEL_MAP, LOGGING_FORMAT, buildinfo
from dpamvifgenerator.controller.mainwindow import MainWindow
from dpamvifgenerator.gui.splashscreen import SplashScreen
from dpamvifgenerator.utility import setup_storage


def get_splash_screen_path():
    root = os.path.abspath(os.path.join(__file__, "..", ".."))
    splash_path = os.path.join(root, "assets", "splash.png")
    return splash_path


def get_app_icon_path():
    root = os.path.abspath(os.path.join(__file__, "..", ".."))
    icon_path = os.path.join(root, "assets", "generator-icon.png")
    return icon_path


def setup_os():
    system = platform.system()
    if system == "win":
        # Set the AppUserModelID so python can update the app's taskbar icon
        from ctypes import windll

        model_id = windll.shell32.SetCurrentProcessExplicitAppUserModelID
        model_id(buildinfo.__bundle__)


class DPAMVIFGeneratorApp(QApplication):
    splash_message = Signal(str)

    def __init__(self):
        super().__init__([])
        self.setWindowIcon(QIcon(get_app_icon_path()))
        self.setStyle("Fusion")

        self.setApplicationName(buildinfo.__product__)
        self.setApplicationDisplayName(buildinfo.__product__)
        self.setApplicationVersion(buildinfo.__version__)

        self.user_data_dir = None
        self.ds = None
        self.widget = None

    def setup(self, kwargs):
        # Setup local storage for app
        self.user_data_dir = setup_storage()
        # Create datastore
        self.ds = shelve.open(
            os.path.join(self.user_data_dir, "{}.db".format(buildinfo.__bundle__))
        )
        # Perform OS specific setup
        setup_os()
        # Create main window to start app
        self.widget = MainWindow(
            ds=self.ds,
            user_data_dir=self.user_data_dir,
            splash_message=self.splash_message.emit,
            **kwargs
        )
        # Connect signals with MainWindow
        self.aboutToQuit.connect(self.widget.app_quitting)

    def start(self):
        self.widget.show()
        self.exec()

    def quit(self):
        self.widget.quit()
        self.ds.close()


def main(**kwargs):
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL_MAP["info"], format=LOGGING_FORMAT, datefmt="%H:%M:%S"
    )

    # Create application and splash screen
    app = DPAMVIFGeneratorApp()
    qdarktheme.setup_theme("auto")
    splash_screen = SplashScreen(
        splash_image_path=get_splash_screen_path(), timeout=0.1
    )
    app.splash_message.connect(splash_screen.update_message)

    # Setup and launch
    app.setup(kwargs)
    splash_screen.launch(app.widget.ui, on_finish=app.start)
