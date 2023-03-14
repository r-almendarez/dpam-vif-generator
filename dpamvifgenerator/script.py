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
        ET.register_namespace("opt", "http://usb.org/VendorInfoFileOptionalContent.xsd")
        ET.register_namespace("vif", "http://usb.org/VendorInfoFile.xsd")
        ET.register_namespace("xsi", "http://www.w3.org/2001/XMLSchema-instance")

        # Load input USBIF VIF XML
        input_vif = DPAMVIFGenerator.load_input_vif(self.in_vif)

        # Load DPAM Settings XML
        dpam_settings = DPAMVIFGenerator.load_dpam_settings(self.settings)

        # Generate DPAM VIF XML file
        DPAMVIFGenerator.generate_dpam_vif(input_vif, dpam_settings)

        # Write out generated XML file
        DPAMVIFGenerator.write_output_vif(input_vif, self.out_vif)

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
        prefix_map = {"vif": "http://usb.org/VendorInfoFile.xsd"}
        port_settings = {}
        for port in dpam_settings.getroot().findall(".//vif:Component", prefix_map):
            port_name = port.find("vif:Port_Label", prefix_map).text
            if not port_name:
                error = "Error: Missing vif:Port_Label from DPAM Settings XML file"
                logging.error(error)
                raise InvalidSettingsXML(error)
            port_settings[port_name] = port.find(".//vif:SOPSVID", prefix_map)

        # Find SOPSVIDList in input VIF tree and insert dpam settings for each port
        for port in input_vif.getroot().findall(".//vif:Component", prefix_map):
            # Find SOPSVIDList
            port_name = port.find("vif:Port_Label", prefix_map).text
            sopsvidlist = port.find("vif:SOPSVIDList", prefix_map)
            # Create list if it does not already exist
            if not sopsvidlist:
                sopsvidlist = ET.Element("vif:SOPSVIDList", prefix_map)
                port.append(sopsvidlist)
            # Check for existing DPAM SVID entry and remove if found
            dpam_svids = sopsvidlist.findall(
                './/vif:SVID_SOP[@value="{}"]...'.format(DPAM_SOP_ID), prefix_map
            )
            [sopsvidlist.remove(dpam_svid) for dpam_svid in dpam_svids]
            # Add in newly generated DPAM SVID settings
            try:
                sopsvidlist.append(port_settings[port_name])
            except KeyError:
                error = (
                    "Error: Could not find settings for {} in "
                    "DPAM Settings XML file".format(port_name)
                )
                logging.error(error)
                raise InvalidSettingsXML(error)

    @staticmethod
    def write_output_vif(generated_vif: ET, out_vif: str):
        ET.indent(generated_vif, space=XML_INDENT, level=0)
        generated_vif.write(out_vif, encoding="utf8", method="xml")


def main(**kwargs):
    # Generate DPAM VIF XML
    generator = DPAMVIFGenerator(**kwargs)
    generator.generate_vif()
