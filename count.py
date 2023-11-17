import xml.etree.ElementTree as ET

def count_line(base_xml_file, tran_xml_file):
    # Parse the XML file
    base_tree = ET.parse(base_xml_file)
    base_root = base_tree.getroot()

    # Parse the XML file
    trans_tree = ET.parse(tran_xml_file)
    trans_root = trans_tree.getroot()

    print(f"Base: {len(base_root.findall('.//content'))} | Tran: {len(trans_root.findall('.//content'))}")

# Usage
base_xml_file = 'C:/Users/namin/Desktop/Mods/vietname/Work/Localization/English/english.xml'
tran_xml_file = 'C:/Users/namin/Desktop/Mods/vietname/Work/Localization/German/english.xml'

count_line(base_xml_file, tran_xml_file)