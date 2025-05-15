"""
Code completion module for ChiX Editor
Provides intelligent code suggestions for C programming
"""

import re
import os
import glob
import tkinter as tk
from collections import defaultdict

# Standard C library functions and keywords
C_STDLIB_FUNCTIONS = [
    "printf", "scanf", "fprintf", "fscanf", "sprintf", "sscanf",
    "fopen", "fclose", "fread", "fwrite", "fseek", "ftell", "rewind",
    "malloc", "calloc", "realloc", "free", "memcpy", "memset", "memmove",
    "strlen", "strcpy", "strncpy", "strcat", "strncat", "strcmp", "strncmp",
    "strchr", "strrchr", "strstr", "strtok", "atoi", "atol", "atof",
    "rand", "srand", "time", "clock", "difftime", "mktime", "localtime",
    "gmtime", "strftime", "exit", "abort", "atexit", "system", "getenv",
    "bsearch", "qsort", "abs", "labs", "div", "ldiv", "sin", "cos", "tan",
    "asin", "acos", "atan", "atan2", "sinh", "cosh", "tanh", "exp", "log",
    "log10", "pow", "sqrt", "ceil", "floor", "fabs", "fmod", "setjmp", "longjmp"
]

C_KEYWORDS = [
    "auto", "break", "case", "char", "const", "continue", "default", "do",
    "double", "else", "enum", "extern", "float", "for", "goto", "if",
    "int", "long", "register", "return", "short", "signed", "sizeof", "static",
    "struct", "switch", "typedef", "union", "unsigned", "void", "volatile",
    "while", "inline", "restrict", "_Bool", "_Complex", "_Imaginary"
]

C_PREPROCESSOR = [
    "#include", "#define", "#undef", "#ifdef", "#ifndef", "#if", "#else",
    "#elif", "#endif", "#error", "#pragma", "#line"
]

C_TYPES = [
    "int", "char", "void", "float", "double", "short", "long", "unsigned",
    "signed", "size_t", "FILE", "time_t", "clock_t", "struct", "union",
    "enum", "const", "static", "extern", "volatile", "register", "restrict",
    "bool", "_Bool", "_Complex", "_Imaginary", "uint8_t", "uint16_t",
    "uint32_t", "uint64_t", "int8_t", "int16_t", "int32_t", "int64_t"
]

# Common C code snippets for autocompletion
C_SNIPPETS = {
    "main": "int main(int argc, char *argv[]) {\n    \n    return 0;\n}",
    "for": "for (int i = 0; i < n; i++) {\n    \n}",
    "while": "while (condition) {\n    \n}",
    "do": "do {\n    \n} while (condition);",
    "if": "if (condition) {\n    \n}",
    "ifelse": "if (condition) {\n    \n} else {\n    \n}",
    "switch": "switch (expression) {\n    case value1:\n        // code\n        break;\n    case value2:\n        // code\n        break;\n    default:\n        // code\n        break;\n}",
    "struct": "struct name {\n    // members\n};",
    "function": "return_type function_name(parameters) {\n    // code\n    return value;\n}",
    "include": "#include <stdio.h>",
    "printf": 'printf("%s\\n", );',
    "scanf": 'scanf("%d", &variable);',
    "malloc": "type *ptr = (type *)malloc(size * sizeof(type));\nif (ptr == NULL) {\n    // Handle error\n}",
    "free": "free(ptr);\nptr = NULL;"
}

class CodeCompleter:
    """Provides code completion functionality for C code"""
    
    def __init__(self):
        """Initialize the code completer"""
        self.project_symbols = {}  # Cache of project symbols
        self.local_variables = {}  # Current file variables
        self.included_headers = set()  # Set of included headers
    
    def _extract_header_name(self, line):
        """Extract header name from #include line"""
        header_match = re.search(r'#include\s+[<"]([^>"]+)[>"]', line)
        if header_match:
            return header_match.group(1)
        return None
    
    def _extract_local_variables(self, text, cursor_pos):
        """Extract local variables from text up to cursor position"""
        # Get text up to cursor
        text_before_cursor = text[:cursor_pos]
        
        # Find variable declarations
        # Simple regex to find C variable declarations (not perfect, but works for basic cases)
        var_pattern = r'\b(int|char|float|double|long|short|unsigned|signed|void|size_t|bool|struct|enum|union)\s+([a-zA-Z_][a-zA-Z0-9_]*)'
        variables = re.findall(var_pattern, text_before_cursor)
        
        # Also look for function parameters
        param_pattern = r'\([^)]*\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?:,|\))'
        params = re.findall(param_pattern, text_before_cursor)
        
        # Combine all found identifiers
        all_vars = [var[1] for var in variables] + params
        
        # Create dictionary with variable name as key and position as value
        result = {}
        for var in all_vars:
            # Find the last occurrence of the variable before cursor
            pos = text_before_cursor.rfind(var)
            if pos >= 0:
                result[var] = pos
        
        return result
    
    def _extract_functions(self, text):
        """Extract function definitions and declarations from text"""
        # Match function declarations/definitions
        func_pattern = r'\b([a-zA-Z_][a-zA-Z0-9_]*\s+)+([a-zA-Z_][a-zA-Z0-9_]*)\s*\([^{;]*\)\s*[{;]'
        funcs = re.findall(func_pattern, text)
        
        result = []
        for func in funcs:
            func_name = func[1].strip()
            if func_name and func_name not in C_KEYWORDS:
                result.append(func_name)
        
        return result
    
    def scan_project_files(self, project_dir):
        """Scan all C files in project to build symbol dictionary"""
        self.project_symbols = defaultdict(list)
        
        # Find all C and header files in project
        c_files = glob.glob(os.path.join(project_dir, "**", "*.c"), recursive=True)
        h_files = glob.glob(os.path.join(project_dir, "**", "*.h"), recursive=True)
        
        # Process all files
        for file_path in c_files + h_files:
            try:
                with open(file_path, 'r') as f:
                    content = f.read()
                    
                # Extract symbols
                funcs = self._extract_functions(content)
                
                # Add to project symbols
                for func in funcs:
                    self.project_symbols[func].append(file_path)
            except Exception as e:
                print(f"Error scanning file {file_path}: {e}")
    
    def get_context(self, text, cursor_pos):
        """Determine context at cursor position"""
        # Get text before cursor
        text_before_cursor = text[:cursor_pos]
        
        # Check if we're inside a string
        # Simple check: count quote marks before cursor
        quote_count = text_before_cursor.count('"') - text_before_cursor.count('\\"')
        if quote_count % 2 == 1:
            return "string"
        
        # Check if we're inside a comment
        if "/*" in text_before_cursor and "*/" not in text_before_cursor[text_before_cursor.rfind("/*"):]:
            return "comment"
        if "//" in text_before_cursor and "\n" not in text_before_cursor[text_before_cursor.rfind("//"):]:
            return "comment"
        
        # Check if preprocessor directive
        last_line_start = text_before_cursor.rfind("\n") + 1
        if "#" in text_before_cursor[last_line_start:]:
            return "preprocessor"
        
        # Check if we're in a function call
        # Simple approach: check if there's an open parenthesis without a matching close
        open_paren = text_before_cursor.rfind("(")
        if open_paren >= 0:
            # Count parentheses after the open one
            close_count = text_before_cursor[open_paren:].count(")")
            open_count = text_before_cursor[open_paren:].count("(")
            if open_count > close_count:
                return "function_args"
        
        # Check for struct member access
        if "->" in text_before_cursor[-5:] or "." in text_before_cursor[-5:]:
            return "struct_member"
        
        # Default to normal code
        return "code"
    
    def get_last_word(self, text, cursor_pos):
        """Get the last word before cursor"""
        text_before_cursor = text[:cursor_pos]
        match = re.search(r'[a-zA-Z0-9_]*$', text_before_cursor)
        if match:
            return match.group(0)
        return ""
    
    def get_completions(self, text, cursor_pos):
        """Get completion suggestions based on context"""
        # Extract context
        context = self.get_context(text, cursor_pos)
        
        # If in a comment or string, don't provide completions
        if context in ["comment", "string"]:
            return []
        
        # Get partial word at cursor
        partial = self.get_last_word(text, cursor_pos)
        if not partial:
            return []
        
        # Update local variables
        self.local_variables = self._extract_local_variables(text, cursor_pos)
        
        # Extract included headers
        self.included_headers = set()
        for line in text.split('\n'):
            header = self._extract_header_name(line)
            if header:
                self.included_headers.add(header)
        
        # Generate completions based on context
        completions = []
        
        # Always check local variables
        for var in self.local_variables:
            if partial.lower() in var.lower():
                completions.append(("variable", var))
        
        # Always check project symbols
        for symbol in self.project_symbols:
            if partial.lower() in symbol.lower():
                completions.append(("function", symbol))
        
        # Context-specific completions
        if context == "preprocessor":
            for directive in C_PREPROCESSOR:
                if partial.lower() in directive.lower():
                    completions.append(("preprocessor", directive))
            
            # If after #include, suggest standard headers
            if "#include" in text[:cursor_pos].split('\n')[-1]:
                std_headers = ["stdio.h", "stdlib.h", "string.h", "math.h", "time.h", "ctype.h"]
                for header in std_headers:
                    if partial.lower() in header.lower():
                        completions.append(("header", header))
        
        elif context == "struct_member":
            # In a real implementation, we'd need to determine the struct type and its members
            # This is a placeholder for now
            pass
        
        elif context == "function_args":
            # Suggest variables of appropriate types
            # This would be more sophisticated in a real implementation
            for var in self.local_variables:
                if partial.lower() in var.lower():
                    completions.append(("variable", var))
        
        else:  # Normal code
            # Keywords
            for keyword in C_KEYWORDS:
                if partial.lower() in keyword.lower():
                    completions.append(("keyword", keyword))
            
            # Types
            for type_name in C_TYPES:
                if partial.lower() in type_name.lower():
                    completions.append(("type", type_name))
            
            # Standard library functions
            for func in C_STDLIB_FUNCTIONS:
                if partial.lower() in func.lower():
                    completions.append(("function", func))
            
            # Snippets
            for snippet_name in C_SNIPPETS:
                if partial.lower() in snippet_name.lower():
                    completions.append(("snippet", snippet_name))
        
        # Sort completions by relevance
        # First exact prefix matches, then contains matches
        exact_matches = [c for c in completions if c[1].lower().startswith(partial.lower())]
        contains_matches = [c for c in completions if not c[1].lower().startswith(partial.lower())]
        
        # Sort each group alphabetically
        exact_matches.sort(key=lambda x: x[1].lower())
        contains_matches.sort(key=lambda x: x[1].lower())
        
        return exact_matches + contains_matches
    
    def apply_completion(self, text, cursor_pos, completion):
        """Apply the selected completion at cursor position"""
        # Get partial word to replace
        partial = self.get_last_word(text, cursor_pos)
        
        comp_type, comp_text = completion
        
        # Calculate new text and cursor position
        text_before = text[:cursor_pos - len(partial)]
        text_after = text[cursor_pos:]
        
        if comp_type == "snippet":
            # Insert snippet
            snippet_content = C_SNIPPETS[comp_text]
            new_text = text_before + snippet_content + text_after
            new_cursor_pos = cursor_pos - len(partial) + snippet_content.find("\n    ") + 5
        else:
            # Insert simple completion
            new_text = text_before + comp_text + text_after
            new_cursor_pos = cursor_pos - len(partial) + len(comp_text)
            
            # Add parentheses for functions
            if comp_type == "function":
                new_text = text_before + comp_text + "()" + text_after
                new_cursor_pos = cursor_pos - len(partial) + len(comp_text) + 1
        
        return new_text, new_cursor_pos

class CompletionPopup:
    """Popup window for displaying code completions"""
    
    def __init__(self, text_widget, completer):
        """Initialize completion popup"""
        self.text_widget = text_widget
        self.completer = completer
        self.popup = None
        self.listbox = None
        self.current_completions = []
    
    def show(self, event=None):
        """Show the completion popup"""
        if hasattr(self.text_widget, "get"):
            # Get current text and cursor position
            text = self.text_widget.get("1.0", "end-1c")
            cursor_index = self.text_widget.index(tk.INSERT)
            line, col = map(int, cursor_index.split("."))
            
            # Calculate absolute cursor position
            cursor_pos = 0
            for i in range(1, line):
                cursor_pos += len(self.text_widget.get(f"{i}.0", f"{i}.end")) + 1
            cursor_pos += col
            
            # Get completions
            self.current_completions = self.completer.get_completions(text, cursor_pos)
            
            if not self.current_completions:
                return self.hide()
            
            # Create popup if it doesn't exist
            if not self.popup:
                self.popup = tk.Toplevel()
                self.popup.withdraw()
                self.popup.overrideredirect(True)
                
                self.listbox = tk.Listbox(self.popup, width=30, height=10, font=("Courier", 10))
                self.listbox.pack(fill="both", expand=True)
                
                # Bind events
                self.listbox.bind("<ButtonRelease-1>", self._on_select)
                self.listbox.bind("<Return>", self._on_select)
                self.listbox.bind("<Escape>", self.hide)
            
            # Clear listbox
            self.listbox.delete(0, tk.END)
            
            # Populate listbox
            max_width = 0
            for comp_type, comp_text in self.current_completions:
                item_text = f"{comp_text:<20} [{comp_type}]"
                self.listbox.insert(tk.END, item_text)
                max_width = max(max_width, len(item_text))
            
            # Position popup near cursor
            x, y, width, height = self.text_widget.bbox(cursor_index)
            x = x + self.text_widget.winfo_rootx()
            y = y + height + self.text_widget.winfo_rooty()
            
            # Adjust popup size
            self.popup.geometry(f"{max(30, max_width * 7)}x200+{x}+{y}")
            
            # Show popup
            self.popup.deiconify()
            self.listbox.selection_set(0)
            self.listbox.focus_set()
    
    def hide(self, event=None):
        """Hide the completion popup"""
        if self.popup:
            self.popup.withdraw()
            # Return focus to text widget
            if self.text_widget:
                self.text_widget.focus_set()
    
    def _on_select(self, event=None):
        """Handle selection from the completion list"""
        if not self.listbox or not self.current_completions:
            return
        
        # Get selected item
        selection = self.listbox.curselection()
        if not selection:
            return
        
        index = selection[0]
        if index < 0 or index >= len(self.current_completions):
            return
        
        # Get completion
        completion = self.current_completions[index]
        
        # Apply completion
        text = self.text_widget.get("1.0", "end-1c")
        cursor_index = self.text_widget.index(tk.INSERT)
        line, col = map(int, cursor_index.split("."))
        
        # Calculate absolute cursor position
        cursor_pos = 0
        for i in range(1, line):
            cursor_pos += len(self.text_widget.get(f"{i}.0", f"{i}.end")) + 1
        cursor_pos += col
        
        # Apply completion
        new_text, new_cursor_pos = self.completer.apply_completion(text, cursor_pos, completion)
        
        # Update text widget
        self.text_widget.delete("1.0", "end")
        self.text_widget.insert("1.0", new_text)
        
        # Set cursor position
        # Convert absolute position back to line:column
        lines = new_text[:new_cursor_pos].split("\n")
        new_line = len(lines)
        new_col = len(lines[-1])
        self.text_widget.mark_set(tk.INSERT, f"{new_line}.{new_col}")
        
        # Hide popup
        self.hide()
        
        # Ensure text widget has focus
        self.text_widget.focus_set()