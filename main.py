import re
from configparser import ConfigParser
from tkinter import (
    BOTH,
    END,
    INSERT,
    LEFT,
    RIGHT,
    VERTICAL,
    X,
    Y,
    Frame,
    IntVar,
    Label,
    Scrollbar,
    Tk,
    filedialog,
    messagebox
)
from tkinter.scrolledtext import ScrolledText
from tkinter.ttk import Checkbutton, Style, Treeview, Button, Entry
from xml.etree import ElementTree as ET
from googletrans import Translator

import pyperclip

from sort import open_sort_dialog
from globals import *

translator = Translator()


def on_submit_edit():
    global table, xml_root, trans_input
    if not hasattr(trans_input, 'editing_item_iid'):
        return None
    selected_iid = trans_input.editing_item_iid
    selected_index = trans_input.editing_item_index

    input_value = trans_input.get('1.0', END).strip().replace('\n', '<br>')
    current_values = table.item(selected_iid).get("values")

    current_values[2] = input_value
    xml_root[selected_index].text = input_value
    table.item(selected_iid, values=current_values, tags=("edited",))

    table.selection_remove(selected_iid)
    table.focus(None)


def on_trans_edit():
    global table, xml_root, trans_input
    if not hasattr(trans_input, 'editing_item_iid'):
        return None
    selected_iid = trans_input.editing_item_iid
    current_values = table.item(selected_iid).get("values")

    result = translator.translate(current_values[3].replace('<br>', '\n'), src='en', dest='vi')
    trans_input.delete('1.0', END)
    trans_input.insert(INSERT, result.text)


def on_revert_edit():
    global table, xml_root, trans_input
    if not hasattr(trans_input, 'editing_item_iid'):
        return None
    selected_iid = trans_input.editing_item_iid
    current_values = table.item(selected_iid).get("values")

    trans_input.delete('1.0', END)
    trans_input.insert(INSERT, current_values[2].replace('<br>', '\n'))


def get_indices(string, char, plus=0):
    indices = []
    current_line = 0
    for i, line in enumerate(string.split("<br>")):
        if char in line:
            index = 0
            current_line = i + 1
            while True:
                try:
                    index = line.index(char, index)
                    indices.append(f"{current_line}.{index + plus}")
                    index += 1
                except ValueError:
                    break
    return indices


def format_text_input(input, value):
    tag_open_chars = get_indices(value, '<')
    tag_close_chars = get_indices(value, '>', 1)
    tag_open_var_chars = get_indices(value, '[')
    tag_close_var_chars = get_indices(value, ']', 1)

    end_tag = 0
    for index, val in enumerate(tag_open_chars):
        input.tag_add("hightlight", f"{val}", f"{tag_close_chars[index]}")
        end_tag += 1
        if end_tag % 2 == 0:
            input.tag_add("hightlight2", f"{tag_close_chars[index-1]}", f"{val}")

    for index, val in enumerate(tag_open_var_chars):
        input.tag_add("hightlight2", f"{val}", f"{tag_close_var_chars[index]}")


def on_edit(event):
    global table, trans_input
    cell = table.identify_row(event.y)
    column = table.identify_column(event.x)
    if not cell:
        return
    # Select and focus on single click
    table.selection_set(cell)
    table.focus(cell)

    # Record item iid
    trans_input.editing_item_iid = cell
    trans_input.editing_item_index = int(table.index(cell))

    # Get select value
    selected = table.selection()[0]
    values = table.item(selected, "values")

    trans_input.delete('1.0', END)
    trans_input.insert(INSERT, values[2].replace('<br>', '\n'))
    format_text_input(trans_input, values[2])

    base_input.configure(state='normal')
    base_input.delete('1.0', END)
    base_input.insert(INSERT, values[3].replace('<br>', '\n'))
    base_input.configure(state='disabled')
    format_text_input(base_input, values[3])

    if column == "#1":
        pyperclip.copy(values[0])
    elif column == '#4':
        pyperclip.copy(values[3])


def load_data():
    global table, xml_root, xml_tree, base_file_entry, trans_file_entry
    if len(table.get_children()):
        table.delete(*table.get_children())

    if base_file_entry.get() and trans_file_entry.get():
        idx = 0
        try:
            xml_tree = ET.parse(trans_file_entry.get())
            xml_root = xml_tree.getroot()

            base_tree = ET.parse(base_file_entry.get())
            base_root = base_tree.getroot()
        except IOError:
            messagebox.showerror(
                "Error", "File does not exist or could not be opened."
            )
            return None

        for elem in base_root:
            trans_elem = xml_root[idx]
            trans_text = trans_elem.text
            if elem.get("contentuid") != trans_elem.get("contentuid"):
                xml_root.insert(idx, elem)
                trans_elem = elem
                trans_text = elem.text

            tags = []
            if elem.text != trans_elem.text:
                tags = ["diff"]

            table.insert(
                "",
                "end",
                text=idx + 1,
                tags=tags,
                values=(
                    elem.get("contentuid"),
                    elem.get("version"),
                    trans_text,
                    elem.text,
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


def select_file(file_entry):
    def wrapper():
        filename = filedialog.askopenfilename(filetypes=[("XML file", ".xml")])
        file_entry.delete(0, 'end')
        file_entry.insert(0, filename)

    return wrapper


def save_file():
    global xml_tree
    if xml_tree:
        output_file = filedialog.asksaveasfilename(defaultextension="xml", filetypes=[("XML file", ".xml")])
        if output_file:
            xml_tree.write(
                output_file, encoding="utf-8", xml_declaration=True
            )
            messagebox.showinfo("Save File", "File saved successfully.")
    else:
        messagebox.showerror("Error", "File not found.")


def get_matches(search_input):
    global match_case, match_reg, match_index, match_un_trans
    search_text = search_input
    if len(search_input) == 0 and match_un_trans.get() == 0:
        return []

    if match_case.get() == 0 and match_reg.get() == 0:
        search_text = search_text.lower()

    data = table.get_children()
    length = len(data)
    for index in range(match_index, length):
        item = data[index]
        values = table.item(item)["values"]

        if match_reg.get() == 0:
            content_id = str(values[0])
            trans = str(values[2])
            base = str(values[3])

            if match_un_trans.get() == 1 and table.tag_has('diff', item):
                continue

            if match_case.get() == 0:
                content_id = content_id.lower()
                trans = trans.lower()
                base = base.lower()

            if search_text in content_id or search_text in trans or search_text in base:
                if index < length - 1:
                    match_index = index + 1
                else:
                    match_index = 0
                return item
        elif (
                re.search(search_text, str(values[0]))
                or re.search(search_text, str(values[2]))
                or re.search(search_text, str(values[3]))
        ):
            if match_un_trans.get() == 1 and table.tag_has('diff', item):
                continue

            if index < length - 1:
                match_index = index + 1
            else:
                match_index = 0
            return item
    match_index = 0
    return None


def on_search_next(event):
    global match_index, previous_match_id

    if previous_match_id is not None:
        table.item(previous_match_id, tags=("",))

    result = get_matches(search_input.get())

    if result:
        previous_match_id = result
        table.see(result)
        table.focus(result)
        table.item(result, tags=("searched",))
    else:
        messagebox.showwarning("Search", "No matching data found.")


def on_search():
    global table, search_input, match_index, previous_match_id

    match_index = 0
    previous_match_id = None
    result = get_matches(search_input.get())

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
    base_file_entry.pack(side=LEFT, fill=X, expand=1, padx=(10, 0), pady=10)
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
    trans_file_entry.pack(side=LEFT, fill=X, expand=1, padx=(10, 0), pady=10)
    # Browse button
    file_button = Button(
        file_frame,
        width=10,
        style="TButton",
        text="Browse...",
        command=select_file(trans_file_entry),
    )
    file_button.pack(side=LEFT, padx=(10, 50), pady=10)

    # Sort button
    sort_button = Button(
        file_frame, width=10, text="Sort", style="TButton", command=open_sort_dialog
    )
    sort_button.pack(side=LEFT, padx=(0, 10), pady=10)

    # Replace button
    validate_button = Button(
        file_frame, width=10, text="Replace", style="TButton", command=None
    )
    validate_button.pack(side=LEFT, padx=(0, 10), pady=10)

    # Load button
    save_button = Button(
        file_frame, width=10, text="Load", style="TButton", command=load_data
    )
    save_button.pack(side=LEFT, padx=(0, 10), pady=10)

    # Save button
    save_button = Button(file_frame, command=save_file, text="Save")
    save_button.pack(side=RIGHT, padx=(0, 20), pady=10)


def init_table():
    global table, window
    # Create table frame
    table_frame = Frame(window)
    table_frame.pack(fill=BOTH, expand=True)

    # Create table and scrollbar
    columns = ("content_id", "version", "content", "origin")
    table = Treeview(table_frame, columns=columns, height=20)
    scrollbar = Scrollbar(table_frame, orient=VERTICAL, command=table.yview)
    table.config(yscrollcommand=scrollbar.set)
    table.pack(side=LEFT, fill=BOTH, expand=True)
    scrollbar.pack(side=RIGHT, fill=Y)

    # tag config
    table.tag_configure("edited", background="#8fce00")
    table.tag_configure("searched", background="#98B3D9")
    table.tag_configure("diff", background="#fcf6e4")

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


def init_search():
    global window, search_input, match_case, match_reg, match_un_trans
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
    match_reg_input.pack(side=LEFT, padx=(0, 10), pady=(10, 0))

    match_un_trans_input = Checkbutton(search_frame, text="Non-translation", variable=match_un_trans)
    match_un_trans_input.pack(side=LEFT, pady=(10, 0))

    # search button
    search_button = Button(
        search_frame, width=10, text="Search", style="TButton", command=on_search
    )
    search_button.pack(side=RIGHT, padx=(10, 20), pady=(10, 0))


def on_scroll(*args):
    global trans_input, base_input
    trans_input.vbar.set(*args)
    base_input.vbar.set(*args)


def yview(*args):
    global trans_input, base_input
    trans_input.yview(*args)
    base_input.yview(*args)


def init_trans_area():
    global window, trans_input, base_input
    edit_frame = Frame(window)
    edit_frame.pack(fill=BOTH, pady=(0, 5))

    trans_input = ScrolledText(edit_frame, height=5, undo=True)
    trans_input.pack(side=LEFT, fill=BOTH, expand=1, pady=(10, 0))
    trans_input.configure(wrap="word")
    trans_input['yscrollcommand'] = on_scroll
    trans_input.vbar.config(command=yview)
    trans_input.tag_config("hightlight", foreground="#1a0dab")
    trans_input.tag_config("hightlight2", foreground="#d94d0e")

    button_frame = Frame(edit_frame)
    button_frame.pack(side=LEFT, padx=5)

    search_button = Button(
        button_frame, width=10, text="Apply", style="TButton", command=on_submit_edit
    )
    search_button.pack(side="top")

    revert_button = Button(
        button_frame, width=10, text="Revert", style="TButton", command=on_revert_edit
    )
    revert_button.pack(side="top", pady=(5, 0))

    trans_button = Button(
        button_frame, width=10, text="Translation", style="TButton", command=on_trans_edit
    )
    trans_button.pack(side="bottom", pady=(5, 0))

    base_input = ScrolledText(edit_frame, height=5)
    base_input.pack(side=RIGHT, fill=BOTH, expand=1, pady=(5, 0))
    base_input.configure(wrap="word")
    base_input['yscrollcommand'] = on_scroll
    base_input.vbar.config(command=yview)
    base_input.tag_config("hightlight", foreground="#1a0dab")
    base_input.tag_config("hightlight2", foreground="#d94d0e")


def init_layout():
    init_search()
    init_action_button()
    init_trans_area()
    init_table()


def load_config():
    config = ConfigParser()
    config.sections()
    config.read("config.ini")
    data = config["DEFAULT"]
    if data["base_path"]:
        base_file_entry.delete(0, 'end')
        base_file_entry.insert(0, str(data["base_path"]))
    if data["trans_path"]:
        trans_file_entry.delete(0, 'end')
        trans_file_entry.insert(0, str(data["trans_path"]))


def load_style():
    style = Style()
    style.configure('.', font=('Calibri', 10))
    style.configure('TButton', activebackground="red")
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


if __name__ == "__main__":
    global window
    # Create Tk window
    window = Tk()
    window.iconbitmap("icon.ico")
    match_case = IntVar()
    match_reg = IntVar()
    match_un_trans = IntVar()
    window.title("Baldur's gate 3 Localization")
    init_layout()
    load_config()
    load_style()

    window.mainloop()
