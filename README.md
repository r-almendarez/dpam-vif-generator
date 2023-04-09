# DPAM VIF Generator

DPAM VIF Generator generates a USBIF/DPAM VIF file based on user inputs for use with test equipment correlation, proper test converage for certification, and at VESA Plugtest events.

**Project Status**
[![Python Versions](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/)
[![Qt Versions](https://img.shields.io/badge/QT-6-blue)](https://www.qt.io/qt-for-python)
[![License](https://img.shields.io/badge/license-MIT-green)](https://github.com/r-almendarez/dpam-vif-generator/blob/main/LICENSE)

## License
This tool is covered under the MIT License. See LICENSE file for full details.

```
Copyright (c) VESA. All rights reserved.
This code is licensed under the MIT License (MIT).
THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
```

___

## High Level Summary
Determining device/port capabilities for USB Type-C DiplayPort Alternate Mode (DPAM) ports and DisplayPort (DP) Source ports is difficult and there is no standard, machine readable format to report this information to test tools. This affects test equipment correlation and proper test coverage for certification and at VESA Plugtest events.

The USB Implementers Forum (USBIF) currently has a Vendor Info File (VIF) tool and documentation for VIF structure/definitions:
+ The USBIF tool can create or load VIF files
+ Had support at one time for DPAM but no longer supported in current tool
+ Supports an "Optional Content Block" but no content is currently included

This tool provides a GUI for quickly populating tester required DPAM content, and generating an updated USBIF VIF that includes DPAM content within each port's Optional Content Block.

___

## Installation
Platform installers can be found under [GitHub Releases](https://github.com/r-almendarez/dpam-vif-generator/releases)

___

## Running from Source
This tool requires Python 3.11 (or newer) and Poetry for running from source.

1. Install Python 3.11 or newer
    - https://www.python.org/downloads/
2. Install Poetry
    - https://python-poetry.org/docs/#installing-with-the-official-installer
3. Run the tool
    - Open a terminal, navigate to the repo directory, and run the following commands:
        - ```poetry install```
        - ```poetry run python ./dpamvifgenerator/main.py```

___

## Usage

This tool can be run as an interactive GUI, or in command-line batch mode. In either mode, the generation flow is the same. The user provides an existing compliant USBIF VIF XML file. The tool inserts DPAM configuration information on a port-basis, and then the tool generates an updated USBIF/DPAM VIF XML file with the DPAM content included under each port's OptionalContent block. 
![generation flow](./assets/read_me_flow.png)

**GUI Mode**
1. User should provide a USBIF VIF XML file under _Input Vendor Info File (VIF)_
2. Configure each port's DPAM capabilities
3. Click **Save As...** under _Generated Vendor Info File (VIF)_ and specify a path to generate the USBIF/DPAM VIF XML file

**Additional Capabilities**
In GUI Mode, the tool can also Export the current DPAM settings the user has configured to its own XML file. This Settings.xml file can then be Imported, to restore the DPAM settings without having to reconfigure each field in the GUI. Additionally, this Settings.xml file can be used to run the tool in Command Line Mode, for automation and scripting.

To Export Settings, click File -> Export Settings...
To Import Settings, click File -> Import Settings...

**Command-Line Mode**
The tool provides the following command-line interface:
| Parameter | Required | Help |
| --- | --- | --- |
| -i, --input | Yes | Path to an existing USB VIF XML file |
| -o, --output | Yes | Path and filename for generated output VIF |
| -s, --settings | Yes | Path to an existing settings.xml | 
| -b, --batch | No | Run tool in batch mode without launching GUI |

Example Usage:
```
./dpamvifgenerator.exe -i ./USBIF_VIF.xml -o ./Output_DPAM_VIF.xml -s ./Settings.xml --batch
```
