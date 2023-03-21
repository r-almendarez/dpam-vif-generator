# DPAM VIF Generator

## High Level Summary
> Problem Statement: Determining device/port capabilities for DPAM ports and DP Source ports is difficult and there is no standard, machine readable format to report this information to test tools. This affects test equipment correlation and proper test coverage for certification and at VESA Plugtest events.

USBIF currently has a VIF tool and documentation for VIF structure/definitions:
+ USBIF tool can create or load VIF files
+ Had support at one time for DPAM but not in current tool
+ Supports an "Optional Content Block" but it does not seem to work
    - Likely not validated and does not currently map to each port

___

## VESA DPAM VIF Tool Features
1. XML format using the same structure and formatting as USBIF VIF
2. Documentation: Include creation of DPAM VIF documentation/spec
    - Tags are unique to DPAM and do not clash with USBIF tags
3. DPAM VIF creation and reader tool
4. DPAM VIF consistency check
    - Checks that VIF matches device capabilities
5. Should be able to append this to a USBIF VIF for a single file read for test equipment

___

## Proposed Development
+ Python GUI DP Capabilities Section
    - DP Source and Sink Capabilities (SOP)
    - DP Cable Capabilities (SOP'/SOP)
+ Windows Only operation
    - Most existing tools provide .exe only
+ User must provide an existing VIF to import
    - DP information must be appended

![generation flow](./assets/read_me_flow.png)

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
