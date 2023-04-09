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

import darkdetect
import qdarktheme
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QApplication

from dpamvifgenerator import LOG_LEVEL_MAP, LOGGING_FORMAT, buildinfo
from dpamvifgenerator.controller.mainwindow import MainWindow
from dpamvifgenerator.gui.splashscreen import SplashScreen
from dpamvifgenerator.utility import setup_storage


def detect_system_theme(default_theme: str) -> str:
    system_theme = darkdetect.theme()
    if system_theme is None:
        logging.debug(
            f'Failed to detect system theme, defaulting to "{default_theme}" theme.'
        )
        return default_theme
    return system_theme.lower()


def get_splash_screen_path(theme: str):
    root = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    splash_file = "vesa_logo_dark.png" if theme == "dark" else "vesa_logo_light.png"
    splash_path = os.path.join(root, "assets", splash_file)
    return splash_path


def get_app_icon_path():
    root = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    icon_path = os.path.join(root, "assets", "displayport_icon.ico")
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
            **kwargs,
        )
        # Connect signals with MainWindow
        self.aboutToQuit.connect(self.widget.app_quitting)

    def start(self):
        self.widget.show()
        self.exec()

    def quit(self):
        self.widget.quit()
        self.ds.close()

    def setup_theme(self) -> str:
        # Setup theme based on OS settings
        qdarktheme.setup_theme("auto")
        theme = detect_system_theme("dark")
        # Set tool tips based on detected theme
        if theme == "dark":
            qdarktheme.setup_theme(additional_qss="QToolTip { border: 0px; }")
        return theme


def main(**kwargs):
    # Configure logging
    logging.basicConfig(
        level=LOG_LEVEL_MAP["info"], format=LOGGING_FORMAT, datefmt="%H:%M:%S"
    )

    # Create application and splash screen
    app = DPAMVIFGeneratorApp()
    # Set theme
    theme = app.setup_theme()
    splash_screen = SplashScreen(
        splash_image_path=get_splash_screen_path(theme),
        timeout=0.1,
        theme=theme,
    )
    app.splash_message.connect(splash_screen.update_message)

    # Setup and launch
    app.setup(kwargs)
    splash_screen.launch(app.widget.ui, on_finish=app.start)
