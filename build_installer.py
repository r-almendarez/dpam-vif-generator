######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import PyInstaller.__main__
import os

PyInstaller.__main__.run(
    [
        "./dpamvifgenerator/main.py",
        "--name",
        "dpamvifgenerator",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--add-data",
        os.path.join("dpamvifgenerator", "uifiles", "mainwindow.ui") + os.pathsep + os.path.join("dpamvifgenerator","uifiles"),
        "--add-data",
        os.path.join("dpamvifgenerator", "uifiles", "about.ui") + os.pathsep + os.path.join("dpamvifgenerator", "uifiles"),
        "--add-data",
        os.path.join("assets", "vesa_logo_dark.png") + os.pathsep + "assets",
        "--add-data",
        os.path.join("assets", "vesa_logo_light.png") + os.pathsep + "assets",
        "--add-data",
        os.path.join("assets", "displayport_icon.ico") + os.pathsep + "assets",
        "--hidden-import=ctypes",
        "--icon=./assets/displayport_icon.ico",
    ]
)
