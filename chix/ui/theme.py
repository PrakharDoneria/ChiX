"""
Theme management for ChiX Editor
"""

import customtkinter as ctk
import json
import os

# Define color schemes
THEMES = {
    # VS Code Dark+ inspired theme
    "vscode_dark": {
        "bg_primary": "#1e1e1e",
        "bg_secondary": "#252526",
        "bg_tertiary": "#2d2d30",
        "bg_hover": "#3e3e42",
        "fg_primary": "#d4d4d4",
        "fg_secondary": "#9e9e9e",
        "accent_primary": "#007acc",
        "accent_secondary": "#3794ff",
        "error": "#f44747",
        "warning": "#ff8800",
        "success": "#35af74",
        "string": "#ce9178",
        "keyword": "#569cd6",
        "comment": "#6A9955",
        "function": "#dcdcaa",
        "type": "#4ec9b0",
        "number": "#b5cea8",
        "operator": "#d4d4d4",
        "variable": "#9cdcfe",
        "class": "#4ec9b0",
        "parameter": "#9cdcfe",
        "line_highlight": "#2a2d2e",
        "selection": "#264f78",
    },
    
    # Xcode Dark theme (inspired by Xcode's dark mode)
    "xcode_dark": {
        "bg_primary": "#292a30",
        "bg_secondary": "#1e1e1e",
        "bg_tertiary": "#252528",
        "bg_hover": "#3a3a3c",
        "fg_primary": "#dfdfe0",
        "fg_secondary": "#9d9d9f",
        "accent_primary": "#4f87ff",
        "accent_secondary": "#6699ff",
        "error": "#ff3b30",
        "warning": "#ff9500",
        "success": "#34c759",
        "string": "#fc6a5d",
        "keyword": "#fc5fa3",
        "comment": "#6c7986",
        "function": "#a167e6",
        "type": "#67b7a4",
        "number": "#d0bf69",
        "operator": "#a9b7c6",
        "variable": "#41a1c0",
        "class": "#5dd8ff",
        "parameter": "#8ec4e6",
        "line_highlight": "#2f3239",
        "selection": "#3f638b",
    },
    
    # Xcode Light theme (inspired by Xcode's light mode)
    "xcode_light": {
        "bg_primary": "#ffffff",
        "bg_secondary": "#f4f4f4",
        "bg_tertiary": "#e8e8e8",
        "bg_hover": "#d9d9d9",
        "fg_primary": "#262626",
        "fg_secondary": "#5b5b5b",
        "accent_primary": "#0f68a0",
        "accent_secondary": "#3a87b4",
        "error": "#d12f1b",
        "warning": "#cf8500",
        "success": "#23882b",
        "string": "#c41a16",
        "keyword": "#9b2393",
        "comment": "#536579",
        "function": "#6c36a9",
        "type": "#0f68a0",
        "number": "#1c00cf",
        "operator": "#000000",
        "variable": "#326d74",
        "class": "#0f68a0",
        "parameter": "#2e6399",
        "line_highlight": "#ecf5ff",
        "selection": "#b2d7ff",
    },
    
    # Dark theme with blue accents
    "dark_blue": {
        "bg_primary": "#1a1a1a",
        "bg_secondary": "#252525",
        "bg_tertiary": "#2d2d2d",
        "bg_hover": "#3e3e42",
        "fg_primary": "#d4d4d4",
        "fg_secondary": "#9e9e9e",
        "accent_primary": "#1e90ff",
        "accent_secondary": "#5b9bd5",
        "error": "#f44747",
        "warning": "#ff8800",
        "success": "#35af74",
        "string": "#ce9178",
        "keyword": "#569cd6",
        "comment": "#6A9955",
        "function": "#dcdcaa",
        "type": "#4ec9b0",
        "number": "#b5cea8",
        "operator": "#d4d4d4",
        "variable": "#9cdcfe",
        "class": "#4ec9b0",
        "parameter": "#9cdcfe",
        "line_highlight": "#2a2d2e",
        "selection": "#264f78",
    }
}

# Current theme - can be changed at runtime
current_theme = "xcode_dark"

def get_theme():
    """Get the current theme colors"""
    return THEMES[current_theme]

def get_color(color_key):
    """Get a specific color from the current theme"""
    theme = get_theme()
    return theme.get(color_key, "#ffffff")

def set_theme(theme_name):
    """Set the active theme"""
    global current_theme
    if theme_name in THEMES:
        current_theme = theme_name
        return True
    return False

def cycle_theme():
    """Cycle through available themes"""
    global current_theme
    theme_keys = list(THEMES.keys())
    current_index = theme_keys.index(current_theme)
    next_index = (current_index + 1) % len(theme_keys)
    current_theme = theme_keys[next_index]
    return current_theme

def setup_theme():
    """Set up the initial theme configuration"""
    # Set appearance mode 
    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
    
    try:
        # Customize button appearance
        ctk.ThemeManager.theme["CTkButton"]["corner_radius"] = 4
        ctk.ThemeManager.theme["CTkButton"]["border_width"] = 0
        
        # Apply theme colors
        theme = get_theme()
        
        # Apply to standard widgets
        ctk.ThemeManager.theme["CTkFrame"]["fg_color"] = [theme["bg_secondary"], theme["bg_secondary"]]
        ctk.ThemeManager.theme["CTkButton"]["fg_color"] = [theme["accent_primary"], theme["accent_primary"]]
        ctk.ThemeManager.theme["CTkButton"]["hover_color"] = [theme["accent_secondary"], theme["accent_secondary"]]
        ctk.ThemeManager.theme["CTkButton"]["text_color"] = [theme["fg_primary"], theme["fg_primary"]]
        
        # Apply to text-based widgets
        ctk.ThemeManager.theme["CTkTextbox"]["fg_color"] = [theme["bg_primary"], theme["bg_primary"]]
        ctk.ThemeManager.theme["CTkTextbox"]["text_color"] = [theme["fg_primary"], theme["fg_primary"]]
        
        # Apply to entry widgets
        ctk.ThemeManager.theme["CTkEntry"]["fg_color"] = [theme["bg_tertiary"], theme["bg_tertiary"]]
        ctk.ThemeManager.theme["CTkEntry"]["text_color"] = [theme["fg_primary"], theme["fg_primary"]]
        
    except (KeyError, AttributeError) as e:
        print(f"Warning: Error setting up theme: {e}")
        pass

def save_theme_preferences(file_path="theme_prefs.json"):
    """Save theme preferences to a file"""
    prefs = {
        "theme": current_theme,
    }
    
    try:
        with open(file_path, 'w') as f:
            json.dump(prefs, f)
    except Exception as e:
        print(f"Error saving theme preferences: {e}")

def load_theme_preferences(file_path="theme_prefs.json"):
    """Load theme preferences from a file"""
    global current_theme
    
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r') as f:
                prefs = json.load(f)
                if "theme" in prefs and prefs["theme"] in THEMES:
                    current_theme = prefs["theme"]
    except Exception as e:
        print(f"Error loading theme preferences: {e}")
