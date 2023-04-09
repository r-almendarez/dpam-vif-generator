######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import PyInstaller.__main__

PyInstaller.__main__.run(
    [
        "./dpamvifgenerator/main.py",
        "--name",
        "dpamvifgenerator",
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--add-data",
        "dpamvifgenerator\\uifiles\\mainwindow.ui;dpamvifgenerator\\uifiles",
        "--add-data",
        "dpamvifgenerator\\uifiles\\about.ui;dpamvifgenerator\\uifiles",
    ]
)
