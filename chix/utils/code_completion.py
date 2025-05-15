"""
Code completion module for ChiX Editor
Provides intelligent code suggestions for C programming
"""

import re
import os
import tkinter as tk
from tkinter import ttk
from chix.ui.theme import get_color

class CodeCompleter:
    """Provides code completion functionality for C code"""
    
    def __init__(self):
        """Initialize the code completer"""
        # Standard C keywords
        self.keywords = [
            "auto", "break", "case", "char", "const", "continue", "default", "do", "double",
            "else", "enum", "extern", "float", "for", "goto", "if", "int", "long", "register",
            "return", "short", "signed", "sizeof", "static", "struct", "switch", "typedef",
            "union", "unsigned", "void", "volatile", "while"
        ]
        
        # Standard C library functions by header
        self.standard_library = {
            "stdio.h": ["printf", "scanf", "fprintf", "fscanf", "sprintf", "sscanf", "fopen", 
                        "fclose", "fread", "fwrite", "fseek", "ftell", "rewind", "fgetc", 
                        "fputc", "fgets", "fputs", "getchar", "putchar", "gets", "puts"],
            "stdlib.h": ["malloc", "calloc", "realloc", "free", "exit", "abort", "atexit", 
                         "system", "getenv", "atoi", "atol", "atof", "strtol", "strtoul", 
                         "strtod", "rand", "srand"],
            "string.h": ["memcpy", "memmove", "memset", "memcmp", "memchr", "strcpy", 
                         "strncpy", "strcat", "strncat", "strcmp", "strncmp", "strchr", 
                         "strrchr", "strstr", "strlen"],
            "math.h": ["sin", "cos", "tan", "asin", "acos", "atan", "atan2", "sinh", 
                       "cosh", "tanh", "exp", "log", "log10", "pow", "sqrt", "ceil", 
                       "floor", "fabs", "ldexp", "frexp", "modf", "fmod"],
            "time.h": ["time", "difftime", "mktime", "asctime", "ctime", "gmtime", 
                       "localtime", "strftime"],
            "ctype.h": ["isalnum", "isalpha", "iscntrl", "isdigit", "isgraph", 
                       "islower", "isprint", "ispunct", "isspace", "isupper", 
                       "isxdigit", "tolower", "toupper"]
        }
        
        # Common C/C++ preprocessor directives
        self.preprocessor = [
            "#include", "#define", "#undef", "#ifdef", "#ifndef", "#if", "#else", 
            "#elif", "#endif", "#error", "#pragma"
        ]
        
        # Standard headers to suggest
        self.standard_headers = [
            "stdio.h", "stdlib.h", "string.h", "math.h", "time.h", "ctype.h",
            "stdarg.h", "errno.h", "float.h", "limits.h", "locale.h", "setjmp.h",
            "signal.h", "stddef.h", "assert.h"
        ]
        
        # Project-specific completions (will be populated dynamically)
        self.project_functions = []
        self.project_variables = []
        self.project_types = []
        self.project_headers = []
    
    def _extract_header_name(self, line):
        """Extract header name from #include line"""
        include_match = re.search(r'#\s*include\s*[<"]([^>"]+)[>"]', line)
        if include_match:
            return include_match.group(1)
        return None
    
    def _extract_local_variables(self, text, cursor_pos):
        """Extract local variables from text up to cursor position"""
        # Find all variable declarations
        local_vars = []
        
        # Simplified pattern to find variable declarations
        var_pattern = r'\b(int|char|float|double|long|short|unsigned|struct|enum)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        for match in re.finditer(var_pattern, text[:cursor_pos]):
            local_vars.append(match.group(2))
        
        return local_vars
    
    def _extract_functions(self, text):
        """Extract function definitions and declarations from text"""
        functions = []
        
        # Pattern to match function declarations/definitions
        func_pattern = r'\b(int|void|char|float|double|long|short|unsigned|struct|enum|\w+)\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(([^)]*)\)'
        for match in re.finditer(func_pattern, text):
            functions.append(match.group(2))
        
        return functions
    
    def scan_project_files(self, project_dir):
        """Scan all C files in project to build symbol dictionary"""
        # Lists to store discovered symbols
        functions = []
        variables = []
        types = []
        headers = []
        
        # Walk through the project directory
        for root, _, files in os.walk(project_dir):
            for file in files:
                if file.endswith('.c') or file.endswith('.h'):
                    try:
                        with open(os.path.join(root, file), 'r') as f:
                            content = f.read()
                            
                            # Extract headers
                            for line in content.split('\n'):
                                header = self._extract_header_name(line)
                                if header and header not in headers:
                                    headers.append(header)
                            
                            # Extract functions
                            funcs = self._extract_functions(content)
                            for func in funcs:
                                if func not in functions:
                                    functions.append(func)
                            
                            # Extract types (simplified)
                            type_pattern = r'\btypedef\s+(?:struct|enum|union)?\s*\{[^}]*\}\s*([a-zA-Z_][a-zA-Z0-9_]*)'
                            for match in re.finditer(type_pattern, content):
                                if match.group(1) not in types:
                                    types.append(match.group(1))
                    except Exception:
                        # Skip files that cannot be read
                        pass
        
        # Update project-specific completions
        self.project_functions = functions
        self.project_headers = headers
        self.project_types = types
    
    def get_context(self, text, cursor_pos):
        """Determine context at cursor position"""
        # Check if we're in an include directive
        line_start = text.rfind('\n', 0, cursor_pos) + 1
        line_end = text.find('\n', cursor_pos)
        if line_end == -1:
            line_end = len(text)
        current_line = text[line_start:line_end]
        
        if re.match(r'^\s*#\s*include', current_line):
            return "include"
        
        # Check if we're after a period (member access)
        if cursor_pos > 0 and text[cursor_pos-1] == '.':
            return "member"
        
        # Check if we're after a preprocessor directive
        if re.match(r'^\s*#', current_line):
            return "preprocessor"
        
        # Default context
        return "general"
    
    def get_last_word(self, text, cursor_pos):
        """Get the last word before cursor"""
        if cursor_pos <= 0:
            return ""
        
        # Find the start of the current word
        word_start = cursor_pos - 1
        while word_start >= 0 and text[word_start].isalnum() or text[word_start] == '_':
            word_start -= 1
        
        return text[word_start+1:cursor_pos]
    
    def get_completions(self, text, cursor_pos):
        """Get completion suggestions based on context"""
        context = self.get_context(text, cursor_pos)
        prefix = self.get_last_word(text, cursor_pos)
        
        completions = []
        
        if context == "include":
            # Suggest header files
            headers = self.standard_headers + self.project_headers
            completions = [h for h in headers if prefix == "" or h.startswith(prefix)]
        
        elif context == "preprocessor":
            # Suggest preprocessor directives
            completions = [d for d in self.preprocessor if prefix == "" or d.startswith(prefix)]
        
        elif context == "member":
            # Try to determine the type and suggest members (simplified implementation)
            # In a real implementation, this would analyze the code to determine object type
            completions = ["member1", "member2", "data", "size", "length", "count"]
        
        else:
            # General context - suggest variables, functions, keywords
            all_symbols = []
            all_symbols.extend(self.keywords)
            all_symbols.extend(self.project_functions)
            all_symbols.extend(self._extract_local_variables(text, cursor_pos))
            
            # Add standard library functions based on included headers
            included_headers = []
            for line in text.split('\n'):
                header = self._extract_header_name(line)
                if header:
                    included_headers.append(header)
            
            for header in included_headers:
                if header in self.standard_library:
                    all_symbols.extend(self.standard_library[header])
            
            # Filter by prefix
            completions = [s for s in all_symbols if prefix == "" or s.startswith(prefix)]
        
        return sorted(set(completions))
    
    def apply_completion(self, text, cursor_pos, completion):
        """Apply the selected completion at cursor position"""
        # Find the start of the word being completed
        word_start = cursor_pos
        while word_start > 0 and (text[word_start-1].isalnum() or text[word_start-1] == '_'):
            word_start -= 1
        
        # Return text with the completion inserted
        return text[:word_start] + completion + text[cursor_pos:]


class CompletionPopup:
    """Popup window for displaying code completions"""
    
    def __init__(self, text_widget, completer):
        """Initialize completion popup"""
        self.text_widget = text_widget
        self.completer = completer
        self.popup = None
        self.listbox = None
    
    def show(self, event=None):
        """Show the completion popup"""
        # Get the text and cursor position
        text = self.text_widget.get("1.0", "end-1c")
        cursor_index = self.text_widget.index("insert")
        line, col = map(int, cursor_index.split("."))
        
        # Calculate cursor position in the text
        cursor_pos = 0
        for i in range(1, line):
            cursor_pos += len(self.text_widget.get(f"{i}.0", f"{i}.end")) + 1
        cursor_pos += col
        
        # Get completions
        completions = self.completer.get_completions(text, cursor_pos)
        
        if not completions:
            self.hide()
            return
        
        # Create or update the popup
        if self.popup:
            self.listbox.delete(0, tk.END)
        else:
            self.popup = tk.Toplevel()
            self.popup.overrideredirect(True)
            self.popup.attributes("-topmost", True)
            
            # Create the listbox
            self.listbox = tk.Listbox(
                self.popup,
                background=get_color("bg_secondary"),
                foreground=get_color("fg_primary"),
                selectbackground=get_color("selection"),
                selectforeground=get_color("fg_primary"),
                font=("Cascadia Code", 12),
                height=min(10, len(completions)),
                width=30
            )
            self.listbox.pack(fill="both", expand=True)
            
            # Scrollbar
            scrollbar = ttk.Scrollbar(self.listbox)
            scrollbar.pack(side="right", fill="y")
            self.listbox.config(yscrollcommand=scrollbar.set)
            scrollbar.config(command=self.listbox.yview)
            
            # Bind selection
            self.listbox.bind("<Double-Button-1>", self._on_select)
            self.listbox.bind("<Return>", self._on_select)
            self.listbox.bind("<Escape>", self.hide)
        
        # Position the popup below the cursor
        x, y, _, height = self.text_widget.bbox("insert")
        x = x + self.text_widget.winfo_rootx()
        y = y + height + self.text_widget.winfo_rooty() + 2
        
        self.popup.geometry(f"+{x}+{y}")
        
        # Fill the listbox
        for item in completions:
            self.listbox.insert(tk.END, item)
        
        # Select the first item
        if self.listbox.size() > 0:
            self.listbox.selection_set(0)
            self.listbox.focus_set()
    
    def hide(self, event=None):
        """Hide the completion popup"""
        if self.popup:
            self.popup.destroy()
            self.popup = None
            self.listbox = None
    
    def _on_select(self, event=None):
        """Handle selection from the completion list"""
        if not self.popup or not self.listbox:
            return
        
        # Get the selected completion
        selection = self.listbox.curselection()
        if not selection:
            self.hide()
            return
        
        completion = self.listbox.get(selection[0])
        
        # Get current text and cursor position
        text = self.text_widget.get("1.0", "end-1c")
        cursor_index = self.text_widget.index("insert")
        line, col = map(int, cursor_index.split("."))
        
        # Calculate cursor position in the text
        cursor_pos = 0
        for i in range(1, line):
            cursor_pos += len(self.text_widget.get(f"{i}.0", f"{i}.end")) + 1
        cursor_pos += col
        
        # Apply the completion
        new_text = self.completer.apply_completion(text, cursor_pos, completion)
        
        # Update the text widget
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", new_text)
        
        # Hide the popup
        self.hide()