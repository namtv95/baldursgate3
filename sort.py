import xml.etree.ElementTree as ET

def sort_xml_by_attribute(xml_file, output_file, attribute_name):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Sort the content elements by the specified attribute
    sorted_content = sorted(root, key=lambda x: (x.tag, x.get(attribute_name)))

    tree_sort = ET.parse(output_sorted_xml_file)
    root_sort = tree_sort.getroot()

    for child in sorted_content:
        root_sort.append(child)

    # Write the sorted XML to the output file
    tree_sort.write(output_file, encoding='utf-8', xml_declaration=True)

# Usage
input_xml_file = 'result/trans_editor.xml'
output_sorted_xml_file = 'result/trans_editor_sort.xml'
attribute_to_sort_by = 'contentuid'

sort_xml_by_attribute(input_xml_file, output_sorted_xml_file, attribute_to_sort_by)