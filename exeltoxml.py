import pandas as pd
import xml.etree.ElementTree as ET

def excel_to_xml(excel_file, xml_file):
    # Read Excel file into a pandas DataFrame
    df = pd.read_excel(excel_file)

    # Create XML structure
    root = ET.Element("contentList")

    for index, row in df.iterrows():
        item_element = ET.SubElement(root, "content")

        for col_name, cell_value in row.items():
            if col_name == 'content':
                item_element.text = str(cell_value).strip()
            if (col_name == 'contentuid'):
                item_element.set("contentuid", str(cell_value).strip())
            if (col_name == 'version'):
                item_element.set("version", str(cell_value).strip())

    # Create ElementTree and write to XML file
    tree = ET.ElementTree(root)
    tree.write(xml_file, encoding='utf-8', xml_declaration=True)

if __name__ == "__main__":
    excel_filename = "trans_3_trans.xlsx"
    xml_filename = "trans_3_trans.xml"

    excel_to_xml(excel_filename, xml_filename)