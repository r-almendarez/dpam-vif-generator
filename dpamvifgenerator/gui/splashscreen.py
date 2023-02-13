import threading
import time

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QSplashScreen


class SplashScreen:
    def __init__(self, splash_image_path, timeout):
        # Setup splash screen image
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
        self.splash.showMessage(message, 0x0084, Qt.black)

    def launch(self, app_ui, on_finish):
        self.timer.join()
        self.splash.finish(app_ui)
        on_finish()
