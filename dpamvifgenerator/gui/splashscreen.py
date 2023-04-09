######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import threading
import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen


class SplashScreen:
    def __init__(self, splash_image_path, timeout, theme):
        # Setup splash screen image
        self.theme = theme
        splash_image = QPixmap(splash_image_path)
        self.splash = QSplashScreen(splash_image, Qt.WindowStaysOnTopHint)
        self.splash.setMask(splash_image.mask())
        self.update_message("Initializing...")
        # Setup splash screen timer thread
        self.timer = threading.Thread(target=lambda: time.sleep(timeout))
        # Run
        self.timer.start()
        self.splash.show()

    def update_message(self, message: str):
        color = Qt.white if self.theme == "dark" else Qt.black
        self.splash.showMessage(message, Qt.AlignHCenter | Qt.AlignBottom, color)

    def launch(self, app_ui, on_finish):
        self.timer.join()
        self.splash.finish(app_ui)
        on_finish()
