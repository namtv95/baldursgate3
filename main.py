from configparser import ConfigParser
import re
from tkinter import (
    BOTH,
    END,
    LEFT,
    RIGHT,
    VERTICAL,
    Y,
    Frame,
    IntVar,
    Label,
    Scrollbar,
    Tk,
    filedialog,
    messagebox,
)
from tkinter.ttk import Checkbutton, Style, Treeview, Button, Entry
from xml.etree import ElementTree as ET

import pyperclip

table = None
window = None
base_file_entry = None
trans_file_entry = None
xml_root = None
xml_tree = None

# search input
search_input = None
match_case = None
match_reg = None
match_index = 0
previous_match_id = None


def on_focus_out(event):
    event.widget.destroy()


def on_submit_edit(event):
    global table, xml_root
    new_text = event.widget.get()
    selected_iid = event.widget.editing_item_iid
    selected_index = event.widget.editing_item_index

    current_values = table.item(selected_iid).get("values")
    current_values[2] = new_text

    xml_root[selected_index].text = new_text
    table.item(selected_iid, values=current_values, tags=("edited",))

    table.selection_remove(selected_iid)
    table.focus(None)

    event.widget.destroy()


def on_edit(event):
    global table
    cell = table.identify_row(event.y)
    column = table.identify_column(event.x)
    if not cell:
        return
    if column == "#3":
        # Select and focus on single click
        table.selection_set(cell)
        table.focus(cell)

        # Put cell into edit mode
        column_box = table.bbox(cell, "#3")
        entry_edit = Entry(table, width=column_box[2], font=("Calibri", 11))

        # Record item iid
        entry_edit.editing_item_iid = cell
        entry_edit.editing_item_index = int(table.index(cell))

        # Get select value
        selected = table.selection()[0]
        values = table.item(selected, "values")

        entry_edit.insert(0, values[2])
        # select text in cell
        entry_edit.select_range(0, END)
        entry_edit.focus()

        # add edit box
        entry_edit.place(
            x=column_box[0], y=column_box[1], w=column_box[2], h=column_box[3]
        )

        # add event on edit
        entry_edit.bind("<FocusOut>", on_focus_out)
        entry_edit.bind("<Return>", on_submit_edit)
    elif column == "#1" or column == '#4':
        # Get select value
        selected = table.selection()[0]
        values = table.item(selected, "values")
        if column == '#1':
            pyperclip.copy(values[0])
        else:
            pyperclip.copy(values[3])




def load_data():
    global table, xml_root, xml_tree, base_file_entry, trans_file_entry
    if len(table.get_children()):
        table.delete(*table.get_children())

    if base_file_entry.get() and trans_file_entry.get():
        idx = 0
        xml_tree = ET.parse(trans_file_entry.get())
        xml_root = xml_tree.getroot()

        base_tree = ET.parse(base_file_entry.get())
        base_root = base_tree.getroot()
        for elem in xml_root:
            base_elem = base_root[idx]
            if elem.get("contentuid") != base_elem.get("contentuid"):
                messagebox.showerror(
                    "Error", "Cannot mapping dataset. There are different in two file."
                )
                break
            tags = []
            if elem.text != base_elem.text:
                tags = ["diff"]
            table.insert(
                "",
                "end",
                text=idx + 1,
                tags=tags,
                values=(
                    elem.get("contentuid"),
                    elem.get("version"),
                    elem.text,
                    base_root[idx].text,
                ),
            )
            idx += 1
        config = ConfigParser()
        config["DEFAULT"] = {
            "base_path": base_file_entry.get(),
            "trans_path": trans_file_entry.get(),
        }
        with open("config.ini", "w") as configfile:
            config.write(configfile)
    else:
        messagebox.showwarning(
            "Select File", "Please select both base and translation files."
        )


def init_table():
    global table, window
    # Create table frame
    table_frame = Frame(window)
    table_frame.pack(fill=BOTH, expand=True)

    # Style
    style = Style()
    style.configure(
        "Treeview",
        background="#fff",
        foreground="#333",
        font=("Calibri", 11),
        borderwidth=2,
        relief="groove",
        rowheight=25,
    )
    style.configure("Treeview.Heading", font=("Calibri", 12, "bold")),

    # Create table and scrollbar
    columns = ("content_id", "version", "content", "origin")
    table = Treeview(table_frame, columns=columns, height=30)
    scrollbar = Scrollbar(table_frame, orient=VERTICAL, command=table.yview)
    table.config(yscrollcommand=scrollbar.set)
    table.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # Handle edit mode
    table.tag_configure("edited", background="#8DC94D")
    table.tag_configure("searched", background="#98B3D9")
    table.tag_configure("diff", background="#EBECFF")

    # Load columns
    table.heading("#0", text="No.")
    table.column("#0", stretch=False, width=50)
    table.heading("content_id", text="Content ID")
    table.column("content_id", stretch=False, width=250)
    table.heading("version", text="Version")
    table.column("version", stretch=False, width=70)
    table.heading("content", text="Content")
    table.column("content", width=700)
    table.heading("origin", text="Origin")
    table.column("origin", width=300)

    # Binding edit cell
    table.bind("<Double-1>", on_edit)


def select_file(file_entry):
    def wrapper():
        filename = filedialog.askopenfilename(filetypes=[("XML file", ".xml")])
        file_entry.insert(0, filename)

    return wrapper


def save_file():
    global xml_tree
    if xml_tree:
        xml_tree.write(
            f"result/trans_editor_result.xml", encoding="utf-8", xml_declaration=True
        )


def get_matches(search_input, take_index):
    global match_case, match_reg
    search_text = search_input
    if len(search_input) == 0:
        return []

    if match_case.get() == 0 and match_reg.get() == 0:
        search_text = search_text.lower()

    index = 0
    for item in table.get_children():
        values = table.item(item)["values"]

        if match_reg.get() == 0:
            if match_case.get() == 0:
                values = str(values).lower()
            else:
                values = str(values)
            if search_text in values:
                if index == take_index:
                    return item
                index += 1
        elif (
            re.search(search_text, str(values[0]))
            or re.search(search_text, str(values[2]))
            or re.search(search_text, str(values[3]))
        ):
            if index == take_index:
                return item
            index += 1

    return None


def on_search_next(event):
    global match_index, previous_match_id
    match_index += 1

    if previous_match_id is not None:
        table.item(previous_match_id, tags=("",))

    result = get_matches(search_input.get(), match_index)

    if result:
        previous_match_id = result
        table.see(result)
        table.focus(result)
        table.item(result, tags=("searched",))
    else:
        messagebox.showwarning("Search", "No matching data found.")
        match_index = 0


def on_search():
    global table, search_input, match_index, previous_match_id
    match_index = 0
    previous_match_id = None
    result = get_matches(search_input.get(), match_index)

    if result:
        previous_match_id = result
        table.see(result)
        table.focus(result)
        table.item(result, tags=("searched",))
    else:
        messagebox.showwarning("Search", "No matching data found.")


def init_action_button():
    global window, base_file_entry, trans_file_entry

    # Container
    file_frame = Frame(window)
    file_frame.pack(fill=BOTH)

    # Input file path
    base_label = Label(file_frame, text="Base:", padx=10, width=5)
    base_label.pack(side=LEFT)
    base_file_entry = Entry(file_frame)
    base_file_entry.pack(side=LEFT, fill=BOTH, expand=1, padx=(10, 0), pady=10)
    # Browse button
    file_button = Button(
        file_frame,
        width=10,
        style="TButton",
        text="Browse...",
        command=select_file(base_file_entry),
    )
    file_button.pack(side=LEFT, padx=10, pady=10)

    # Input file path
    trans_label = Label(file_frame, text="Translation:", padx=10)
    trans_label.pack(side=LEFT)
    trans_file_entry = Entry(file_frame)
    trans_file_entry.pack(side=LEFT, fill=BOTH, expand=1, padx=(10, 0), pady=10)
    # Browse button
    file_button = Button(
        file_frame,
        width=10,
        style="TButton",
        text="Browse...",
        command=select_file(trans_file_entry),
    )
    file_button.pack(side=LEFT, padx=(10, 50), pady=10)

    # Load button
    save_button = Button(
        file_frame, width=10, text="Load", style="TButton", command=load_data
    )
    save_button.pack(side=LEFT, padx=(0, 10), pady=10)

    # Save button
    save_button = Button(
        file_frame, width=10, text="Save", style="TButton", command=save_file
    )
    save_button.pack(side=RIGHT, padx=(0, 20), pady=10)


def init_search():
    global window, search_input, match_case, match_reg
    search_frame = Frame(window)
    search_frame.pack(fill=BOTH)

    content_id_label = Label(search_frame, text="Search:", padx=10, width=5)
    content_id_label.pack(side=LEFT, pady=(10, 0))
    search_input = Entry(search_frame)
    search_input.pack(side=LEFT, fill=BOTH, expand=1, padx=(10, 20), pady=(10, 0))
    search_input.bind("<Return>", on_search_next)

    match_case_input = Checkbutton(search_frame, text="Match case", variable=match_case)
    match_case_input.pack(side=LEFT, padx=(0, 10), pady=(10, 0))

    match_reg_input = Checkbutton(search_frame, text="Regex", variable=match_reg)
    match_reg_input.pack(side=LEFT, pady=(10, 0))

    # Save button
    save_button = Button(
        search_frame, width=10, text="Search", style="TButton", command=on_search
    )
    save_button.pack(side=RIGHT, padx=(10, 20), pady=(10, 0))


def init_layout():
    init_search()
    init_action_button()
    init_table()


def load_config():
    config = ConfigParser()
    config.sections()
    config.read("config.ini")
    data = config["DEFAULT"]
    if data["base_path"]:
        base_file_entry.insert(0, str(data["base_path"]))
    if data["trans_path"]:
        trans_file_entry.insert(0, str(data["trans_path"]))


if __name__ == "__main__":
    # Create Tk window
    window = Tk()
    window.iconbitmap("icon.ico")
    match_case = IntVar()
    match_reg = IntVar()
    window.title("Baldur's gate 3 Localization")
    init_layout()
    load_config()

    window.mainloop()
