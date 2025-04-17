from pygments import lex
from pygments.lexers import CLexer
from pygments.styles import get_style_by_name

style = get_style_by_name("monokai")

def highlight(editor):
    code = editor.get("1.0", "end-1c")
    editor.tag_remove("Token", "1.0", "end")
    for token, content in lex(code, CLexer()):
        color = style.style_for_token(token).get("color")
        if color:
            start = editor.search(content, "1.0", stopindex="end", regexp=False)
            while start:
                end = f"{start}+{len(content)}c"
                editor.tag_add("Token", start, end)
                editor.tag_config("Token", foreground=f"#{color}")
                start = editor.search(content, end, stopindex="end", regexp=False)
