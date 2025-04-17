from tkinter import filedialog

def new_file(state):
    state["current_file"] = None
    state["editor"].delete("1.0", "end")
    state["output"].delete("1.0", "end")

def open_file(state, highlight):
    path = filedialog.askopenfilename(filetypes=[("C Files", "*.c")])
    if path:
        with open(path, "r") as file:
            code = file.read()
            state["editor"].delete("1.0", "end")
            state["editor"].insert("1.0", code)
            state["current_file"] = path
            highlight(state["editor"])

def save_file(state):
    if state["current_file"]:
        with open(state["current_file"], "w") as file:
            file.write(state["editor"].get("1.0", "end-1c"))
    else:
        save_file_as(state)

def save_file_as(state):
    path = filedialog.asksaveasfilename(defaultextension=".c", filetypes=[("C Files", "*.c")])
    if path:
        state["current_file"] = path
        with open(path, "w") as file:
            file.write(state["editor"].get("1.0", "end-1c"))
