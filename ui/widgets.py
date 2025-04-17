import customtkinter as ctk
from core.file_ops import new_file, open_file, save_file, save_file_as
from core.runner import run_code
from utils.highlighter import highlight

def create_editor(parent):
    editor = ctk.CTkTextbox(parent, font=("Consolas", 14), wrap="none")
    editor.pack(fill="both", expand=True, padx=10, pady=(10, 5))
    return editor

def create_output(parent):
    output = ctk.CTkTextbox(parent, height=130, font=("Consolas", 12), text_color="lime")
    output.pack(fill="x", padx=10, pady=(0, 10))
    return output

def create_menu(parent, state):
    frame = ctk.CTkFrame(parent, height=40, fg_color="#1e1e1e")  # dark toolbar style
    frame.pack(fill="x", padx=0, pady=0)

    button_style = {
        "corner_radius": 0,
        "height": 32,
        "fg_color": "#2d2d30",
        "hover_color": "#3e3e42",
        "text_color": "white"
    }

    ctk.CTkButton(frame, text="New", command=lambda: new_file(state), **button_style).pack(side="left", padx=(10, 4))
    ctk.CTkButton(frame, text="Open", command=lambda: open_file(state, highlight), **button_style).pack(side="left", padx=4)
    ctk.CTkButton(frame, text="Save", command=lambda: save_file(state), **button_style).pack(side="left", padx=4)
    ctk.CTkButton(frame, text="Save As", command=lambda: save_file_as(state), **button_style).pack(side="left", padx=4)
    ctk.CTkButton(frame, text="Compile & Run", command=lambda: run_code(state), **button_style).pack(side="left", padx=(10, 4))
