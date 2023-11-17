import xml.etree.ElementTree as ET

def fix_uuid(base_filename, tran_filename):
    base_tree = ET.parse(base_filename)
    base_root = base_tree.getroot()

    trans_tree = ET.parse(tran_filename)
    trans_root = trans_tree.getroot()


    # Extract attribute values from the first XML file
    attributes_set_file1 = {elem.get('contentuid') for elem in base_root.findall(f'.//content')}

    # Extract attribute values from the second XML file
    attributes_set_file2 = {elem.get('contentuid') for elem in trans_root.findall(f'.//content')}

    # Find missing attributes in the second XML file
    missing_attributes = attributes_set_file1 - attributes_set_file2

    print(f"Missing attributes in {missing_attributes}")

if __name__ == "__main__":
    tran_filename = "result/trans_editor.xml"
    base_filename = "english_sort.xml"

    fix_uuid(base_filename, tran_filename)