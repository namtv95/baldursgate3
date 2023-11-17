from googletrans import Translator
import xml.etree.ElementTree as ET
import threading

# Create a list to store thread objects
threads = []

translate_exclude = ["&lt;", "&gt;"]


def translate_text(text, target_language):
    translator = Translator()
    translation = translator.translate(text, dest=target_language)
    return translation.text


def translate_and_replace(file_index):
    # Parse the XML file
    tree = ET.parse(f"input/english_{file_index}.xml")
    root = tree.getroot()

    # Iterate through elements and replace text with translations
    idx = 0
    for elem in root.iter():
        if (
            elem.text is not None
            and "LSTag" not in elem.text
            and (
                "." in elem.text
                or "?" in elem.text
                or "!" in elem.text
            )
        ):
            print(f"File {file_index}: {round(100 / 5000 * idx, 2)}")
            translated_text = translate_text(elem.text, "vi")
            elem.text = translated_text
        idx+=1

    # Write the updated XML to the file
    tree.write(
        f"result/english_{file_index}.xml", encoding="utf-8", xml_declaration=True
    )


def main():
    for i in range(1, 75):
        thread = threading.Thread(target=translate_and_replace, args=(i,))
        threads.append(thread)
        thread.start()
    # Wait for all threads to finish
    for thread in threads:
        thread.join()
    print("All threads have finished.")


main()
