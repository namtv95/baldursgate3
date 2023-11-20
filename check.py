import xml.etree.ElementTree as ET

def check_content_id(base_filename, tran_filename):
    base_tree = ET.parse(base_filename)
    base_root = base_tree.getroot()

    trans_tree = ET.parse(tran_filename)
    trans_root = trans_tree.getroot()

    index= 0
    count = 0
    for item in trans_root.iter():
        id = str(item.get('contentuid'))
        if id != 'None':
            base_id = str(base_root[index].get('contentuid'))
            if id != base_id:
                # item.set('contentuid', base_id)
                count+=1
                print(f"{id} <> {base_id}")
                break
            index+=1
    print(count)
    # trans_tree.write(
    #     f"result/trans_editor.xml", encoding="utf-8", xml_declaration=True
    # )
