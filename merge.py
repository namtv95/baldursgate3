import xml.etree.ElementTree as ET

# Load merged.xml
tree_merged = ET.parse('english_result.xml')
root_merged = tree_merged.getroot()

for index in range(1, 45):
    tree = ET.parse(f'result/english_{index}.xml')
    root_child = tree.getroot()
    for child in root_child:
        root_merged.append(child)
        
# Save the merged XML file
tree_merged.write('english_result.xml', encoding='utf-8', xml_declaration=True)