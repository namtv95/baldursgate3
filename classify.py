import xml.etree.ElementTree as ET

def split_xml(input_file, output_file1, output_file2):
    tree = ET.parse(input_file)
    root = tree.getroot()

    # Create new XML trees for each condition
    tree1 = ET.ElementTree(ET.Element("root"))
    root1 = tree1.getroot()

    tree2 = ET.ElementTree(ET.Element("root"))
    root2 = tree2.getroot()

    for item in root.iter():
        if (item.text is not None):  
            if "LSTag" not in item.text and ("." in item.text or "?" in item.text or "!" in item.text):
                # Copy the item to the first output file
                root1.append(item)
            else:
                # Copy the item to the second output file
                root2.append(item)

    # Save the new XML trees to files
    tree1.write(output_file1)
    tree2.write(output_file2)

if __name__ == "__main__":
    input_filename = "english.xml"
    output_filename1 = "trans.xml"
    output_filename2 = "not_trans.xml"

    split_xml(input_filename, output_filename1, output_filename2)