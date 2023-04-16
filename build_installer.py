######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import glob
import os

import PyInstaller.__main__

from dpamvifgenerator.utility import get_asset_file_path


def generate_pdf_args():
    pdfs = glob.glob(get_asset_file_path("assets", "DPAM_VIF_Spec*.pdf"))
    # Add PDF files to build data
    for pdf in pdfs:
        yield "--add-data"
        yield pdf + os.pathsep + "assets"


PyInstaller.__main__.run(
    [
        # Script Main
        "./dpamvifgenerator/main.py",
        "--name",
        "dpamvifgenerator",
        "--onefile",
        "--windowed",
        "--noconfirm",
        # GUI UI Files
        "--add-data",
        os.path.join("dpamvifgenerator", "uifiles", "mainwindow.ui")
        + os.pathsep
        + os.path.join("dpamvifgenerator", "uifiles"),
        "--add-data",
        os.path.join("dpamvifgenerator", "uifiles", "about.ui")
        + os.pathsep
        + os.path.join("dpamvifgenerator", "uifiles"),
        # GUI Splash and Icons
        "--add-data",
        os.path.join("assets", "vesa_logo_dark.png") + os.pathsep + "assets",
        "--add-data",
        os.path.join("assets", "vesa_logo_light.png") + os.pathsep + "assets",
        "--add-data",
        os.path.join("assets", "displayport_icon.ico") + os.pathsep + "assets",
        # DPAM VIF Spec PDFs
        *list(generate_pdf_args()),
        # Function Imports
        "--hidden-import=ctypes",
        # Icon
        "--icon=./assets/displayport_icon.ico",
    ]
)
