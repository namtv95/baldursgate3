import xml.etree.ElementTree as ET

def split_xml(input_file, batch_size):
    # Parse the input XML file
    tree = ET.parse(input_file)
    root = tree.getroot()
    index = 1
    # Iterate through top-level elements in batches
    for i in range(0, len(root), batch_size):
        # Create a new root element for the batch
        batch_root = ET.Element(root.tag)

        # Append elements to the batch
        for element in root[i:i + batch_size]:
            batch_root.append(element)

        # Create a new tree with the batch root
        new_tree = ET.ElementTree(batch_root)

        # Define the output file name based on the batch
        output_file = f'trans_{index}.xml'

        # Write the new tree to the output file
        new_tree.write(output_file, encoding='utf-8', xml_declaration=True)
        index+=1

# Usage
split_xml('trans.xml', batch_size=60000)