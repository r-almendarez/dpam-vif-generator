######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import errno
import os
import platform
import subprocess

import appdirs
from PySide6.QtCore import QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from PySide6.QtWidgets import QWidget

from dpamvifgenerator import buildinfo

# Utility Consts
XML_INDENT = "  "


# Utility Functions
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


def get_asset_file_path(dir_name: str, file_name: str) -> str:
    """Get the path to an asset file to be used by app"""
    root = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
    return os.path.join(root, dir_name, file_name)


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


def open_file_native(file_path: str):
    """Opens a file using the OS's default application"""
    platform_system = platform.system()
    if platform_system == "Darwin":  # macOS
        subprocess.call(("open", file_path))
    elif platform_system == "Windows":  # Windows
        os.startfile(file_path)
    else:  # Linux variants
        subprocess.call(("xdg-open", file_path))
