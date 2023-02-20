import errno
import os

import appdirs
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget

from dpamvifgenerator import buildinfo


def setup_storage() -> str:
    """Setup local storage for saving files temporarily"""
    directories = appdirs.AppDirs(buildinfo.__product__, buildinfo.__company__)
    # Create user data dir for storing app persistent data
    user_data_dir = directories.user_data_dir
    try:
        os.makedirs(user_data_dir)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    # Return path
    return user_data_dir


def get_data_file_path(dir_name: str, file_name: str) -> str:
    """Get the path to a data file to be used by app"""
    root = os.path.abspath(os.path.join(__file__, "..", ".."))
    return os.path.join(root, dir_name, file_name)


def load_ui_file(ui_file_path: str) -> QWidget:
    """Load a Qt UI file and return as a QWidget window handle"""
    ui_file = QFile(ui_file_path)
    if not ui_file.open(QIODevice.ReadOnly):
        print(f"Cannot open {ui_file_path}: {ui_file.errorString()}")
        raise
    loader = QUiLoader()
    window = loader.load(ui_file)
    ui_file.close()
    if not window:
        print(loader.errorString())
        raise
    return window
