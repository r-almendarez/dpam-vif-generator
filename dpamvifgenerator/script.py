######################################################
# Copyright (c) VESA. All rights reserved.
# This code is licensed under the MIT License (MIT).
# THIS CODE IS PROVIDED *AS IS* WITHOUT WARRANTY OF
# ANY KIND, EITHER EXPRESS OR IMPLIED, INCLUDING ANY
# IMPLIED WARRANTIES OF FITNESS FOR A PARTICULAR
# PURPOSE, MERCHANTABILITY, OR NON-INFRINGEMENT.
######################################################
import logging
from xml.etree import ElementTree as ET

from dpamvifgenerator.utility import XML_INDENT

# Consts
DPAM_SOP_ID = 65281  # 0xFF01


# Exception Classes
class MissingGeneratorArg(Exception):
    pass


class InvalidInputVIF(Exception):
    pass


class InvalidSettingsXML(Exception):
    pass


# DPAM VIF Generator Class
class DPAMVIFGenerator:
    def __init__(self, **kwargs):
        # Load arguments from user
        try:
            [
                setattr(self, key, kwargs[key])
                for key in ["in_vif", "out_vif", "settings"]
            ]
        except KeyError as e:
            error = "Error: Missing DPAMVIFGenerator argument. {}".format(e)
            logging.error(error)
            raise MissingGeneratorArg(error)

    def generate_vif(self):
        # Register namespaces
        for name, namespace in DPAMVIFGenerator.get_prefix_map().items():
            ET.register_namespace(name, namespace)

        # Load input USBIF VIF XML
        input_vif = DPAMVIFGenerator.load_input_vif(self.in_vif)

        # Load DPAM Settings XML
        dpam_settings = DPAMVIFGenerator.load_dpam_settings(self.settings)

        # Generate DPAM VIF XML file
        DPAMVIFGenerator.generate_dpam_vif(input_vif, dpam_settings)

        # Write out generated XML file
        DPAMVIFGenerator.write_output_vif(input_vif, self.out_vif)

    @staticmethod
    def get_prefix_map() -> dict:
        return {
            "vif": "http://usb.org/VendorInfoFile.xsd",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance",
            "opt": "http://usb.org/VendorInfoFileOptionalContent.xsd",
        }

    @staticmethod
    def load_input_vif(in_vif: str) -> ET:
        try:
            return ET.parse(
                in_vif, parser=ET.XMLParser(target=ET.TreeBuilder(insert_comments=True))
            )
        except Exception as e:
            error = (
                "Error: Invalid Input USBIF VIF XML file "
                "provided at path: {}. {}".format(in_vif, e)
            )
            logging.error(error)
            raise InvalidInputVIF(error)

    @staticmethod
    def load_dpam_settings(settings: str) -> ET:
        try:
            return ET.parse(settings)
        except Exception as e:
            error = (
                "Error: Invalid DPAM Settings XML file provided at path: {}. {}".format(
                    settings, e
                )
            )
            logging.error(error)
            raise InvalidSettingsXML(error)

    @staticmethod
    def generate_dpam_vif(input_vif: ET, dpam_settings: ET):
        # Get port DPAM settings from DPAM Settings XML
        prefix_map = DPAMVIFGenerator.get_prefix_map()
        port_settings = {}
        for port in dpam_settings.getroot().findall(".//vif:Component", prefix_map):
            port_name = port.find("vif:Port_Label", prefix_map).text
            if not port_name:
                error = "Error: Missing vif:Port_Label from DPAM Settings XML file"
                logging.error(error)
                raise InvalidSettingsXML(error)
            port_settings[port_name] = port.find(".//opt:OptionalContent", prefix_map)

        # Insert DPAM Opt Content blocks on each port
        for port in input_vif.getroot().findall(".//vif:Component", prefix_map):
            port_name = port.find("vif:Port_Label", prefix_map).text
            # Check for existing optional content
            optional_content = port.find("opt:OptionalContent", prefix_map)
            if optional_content:
                # Merge DPAM opt content since OptionalContent block already exists
                optional_content.append(port_settings[port_name])
            else:
                # No existing OptionalContent, so use DPAM version as is
                port.append(port_settings[port_name])

    @staticmethod
    def write_output_vif(generated_vif: ET, out_vif: str):
        ET.indent(generated_vif, space=XML_INDENT, level=0)
        generated_vif.write(out_vif, encoding="utf8", method="xml")


def main(**kwargs):
    # Generate DPAM VIF XML
    generator = DPAMVIFGenerator(**kwargs)
    generator.generate_vif()
