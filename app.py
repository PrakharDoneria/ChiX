import customtkinter as ctk
from ui.theme import setup_theme
from ui.widgets import create_editor, create_output, create_menu
from utils.highlighter import highlight

app = ctk.CTk()
app.geometry("1000x750")
app.title("C Code Editor & Runner")

setup_theme()

# Shared state
state = {
    "current_file": None,
    "editor": None,
    "output": None,
}

# === Toolbar Menu (Top) ===
create_menu(app, state)

# === Main Frame (Editor + Output) ===
main_frame = ctk.CTkFrame(app)
main_frame.pack(fill="both", expand=True)

# === Code Editor (Middle) ===
state["editor"] = create_editor(main_frame)

# === Output Console (Bottom) ===
state["output"] = create_output(main_frame)

# === Default Template ===
starter = """#include <stdio.h>

int main() {
    int x;
    printf("Enter a number: ");
    scanf("%d", &x);
    printf("You entered: %d\\n", x);
    return 0;
}
"""
state["editor"].insert("1.0", starter)
highlight(state["editor"])

app.mainloop()
