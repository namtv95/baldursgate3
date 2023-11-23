from tkinter import BOTH, LEFT, RIGHT, X, Entry, Frame, Label, Tk, Toplevel, filedialog, messagebox
from tkinter.ttk import Button
import xml.etree.ElementTree as ET
from globals import *

dialog = None
filename = None


def get_file():
    global filename
    filepath = filedialog.askopenfilename(filetypes=[("XML file", ".xml")])
    if filepath:
        filename.delete(0, 'end')
        filename.insert(0, filepath)


def open_sort_dialog():
    global dialog, filename, window

    # Open dialog
    dialog = Toplevel()
    width = 500
    height = 30
    screen_width = dialog.master.winfo_screenwidth()
    screen_height = dialog.master.winfo_screenheight()
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    dialog.geometry("%dx%d+%d+%d" % (width, height, x, y))
    dialog.transient(window)
    dialog.grab_set()

    # Add UI elements
    file_frame = Frame(dialog)
    file_frame.pack(fill=BOTH)

    label = Label(file_frame, text="File:", padx=10)
    label.pack(side=LEFT)

    filename = Entry(file_frame)
    filename.pack(side=LEFT, fill=X, expand=1, padx=(10, 0))

    open_button = Button(file_frame, text="Browse", style="TButton", command=get_file)
    open_button.pack(side=LEFT, padx=(10, 0))

    sort_button = Button(file_frame, text="Sort", style="TButton", command=sort_xml_by_attribute)
    sort_button.pack(side=RIGHT, padx=10)

    # Block code execution until window is closed
    dialog.wait_window()


def sort_xml_by_attribute():
    global dialog
    output_file = filedialog.asksaveasfilename(defaultextension="xml", filetypes=[("XML file", ".xml")])
    if not output_file:
        return None

    attribute_name = 'contentuid'
    xml_file = filename.get()

    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Sort the content elements by the specified attribute
    sorted_content = sorted(root, key=lambda x: (x.tag, x.get(attribute_name)))

    sort_root = ET.Element("contentList")
    for child in sorted_content:
        sort_root.append(child)

    sort_tree = ET.ElementTree(sort_root)

    # Write the sorted XML to the output file
    sort_tree.write(output_file, encoding='utf-8', xml_declaration=True)
    dialog.destroy()
    messagebox.showinfo("Sort File", "Sort file successfully.")
