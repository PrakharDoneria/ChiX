"""
File explorer panel for ChiX Editor
"""

import customtkinter as ctk
import tkinter as tk
import os
from chix.ui.theme import get_color
from chix.ui.widgets import ClickableLabel
from chix.utils.git_manager import GitManager
import re

class FileTreeNode:
    """Represents a node in the file tree"""
    
    def __init__(self, path, is_dir=False, parent=None):
        self.path = path
        self.name = os.path.basename(path) or path  # Use path for root
        self.is_dir = is_dir
        self.parent = parent
        self.children = []
        self.expanded = False
    
    def add_child(self, child):
        """Add a child node"""
        self.children.append(child)
    
    def get_children(self):
        """Get sorted children (directories first, then files)"""
        dirs = [c for c in self.children if c.is_dir]
        files = [c for c in self.children if not c.is_dir]
        
        # Sort directories and files alphabetically
        dirs.sort(key=lambda x: x.name.lower())
        files.sort(key=lambda x: x.name.lower())
        
        return dirs + files
    
    def toggle_expanded(self):
        """Toggle expanded state"""
        self.expanded = not self.expanded
        return self.expanded

class FileExplorer(ctk.CTkFrame):
    """
    File explorer panel showing directory structure
    """
    
    def __init__(self, parent, state, **kwargs):
        super().__init__(parent, **kwargs)
        
        self.state = state
        self.root_path = state.get("current_directory", os.getcwd())
        self.tree_root = None
        
        # Initialize Git manager
        self.git_manager = GitManager(self.root_path)
        self.show_git_status = True
        
        # Create UI elements
        self._create_widgets()
        
        # Load initial directory
        self.load_directory(self.root_path)
    
    def _create_widgets(self):
        """Create all UI widgets"""
        # Explorer header - Xcode style
        header_frame = ctk.CTkFrame(self, height=35, fg_color=get_color("bg_secondary"))
        header_frame.pack(fill="x", side="top")
        
        # Title with Xcode-style
        ctk.CTkLabel(
            header_frame,
            text="PROJECT NAVIGATOR",
            font=("SF Pro", 12, "bold"),
            text_color=get_color("fg_secondary"),
            anchor="w"
        ).pack(side="left", padx=10, pady=8)
        
        # Control buttons in Xcode style
        buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        buttons_frame.pack(side="right", padx=8)
        
        # New file button with Xcode styling
        new_file_btn = ctk.CTkButton(
            buttons_frame,
            text="+",
            width=28,
            height=22,
            corner_radius=6,
            fg_color=get_color("bg_tertiary"),
            hover_color=get_color("bg_hover"),
            text_color=get_color("accent_primary"),
            font=("SF Pro", 14, "bold"),
            command=self._new_file
        )
        new_file_btn.pack(side="right", padx=3)
        
        # Refresh button with Xcode styling
        refresh_btn = ctk.CTkButton(
            buttons_frame,
            text="↻",
            width=28,
            height=22,
            corner_radius=6,
            fg_color=get_color("bg_tertiary"),
            hover_color=get_color("bg_hover"),
            text_color=get_color("accent_primary"),
            font=("SF Pro", 14),
            command=self._refresh
        )
        refresh_btn.pack(side="right", padx=3)
        
        # Git branch info section
        self.branch_frame = ctk.CTkFrame(self, height=25, fg_color=get_color("bg_secondary"))
        self.branch_frame.pack(fill="x", side="top")
        
        # Branch icon
        branch_icon = ctk.CTkLabel(
            self.branch_frame,
            text="⑂",  # Git branch symbol
            font=("Arial", 14),
            width=20,
            text_color=get_color("accent_primary")
        )
        branch_icon.pack(side="left", padx=(10, 0))
        
        # Branch name - Initialize with placeholder, then update it
        self.branch_label = ctk.CTkLabel(
            self.branch_frame,
            text="Checking...",
            font=("Arial", 11),
            anchor="w"
        )
        
        # Update after initialization
        self.after(100, lambda: self.branch_label.configure(text=self._get_branch_name()))
        self.branch_label.pack(side="left", padx=(0, 10), fill="x", expand=True)
        
        # Git status toggle button
        self.git_toggle_btn = ctk.CTkButton(
            self.branch_frame,
            text="↻",
            width=25,
            height=20,
            corner_radius=4,
            command=self._refresh_git_status
        )
        self.git_toggle_btn.pack(side="right", padx=5)
        
        # Hide branch frame if not a git repository
        if not self.git_manager.is_git_repo():
            self.branch_frame.pack_forget()
        
        # Path display/selector
        path_frame = ctk.CTkFrame(self, height=30, fg_color="transparent")
        path_frame.pack(fill="x", side="top", padx=5, pady=5)
        
        self.path_var = tk.StringVar(value=self.root_path)
        path_entry = ctk.CTkEntry(
            path_frame,
            textvariable=self.path_var
        )
        path_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        # Go button for path
        go_btn = ctk.CTkButton(
            path_frame,
            text="Go",
            width=40,
            command=self._go_to_path
        )
        go_btn.pack(side="right")
        
        # Tree container with scrollbar
        tree_frame = ctk.CTkFrame(self, fg_color="transparent")
        tree_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        # Scrollable container
        self.canvas = ctk.CTkCanvas(
            tree_frame,
            bg=get_color("bg_primary"),
            highlightthickness=0
        )
        scrollbar = ctk.CTkScrollbar(tree_frame, command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        # Pack canvas and scrollbar
        scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        
        # Create tree container frame
        self.tree_frame = ctk.CTkFrame(self.canvas, fg_color=get_color("bg_primary"))
        self.canvas_window = self.canvas.create_window(
            (0, 0),
            window=self.tree_frame,
            anchor="nw",
            tags="tree"
        )
        
        # Configure canvas and frame events
        self.tree_frame.bind("<Configure>", self._on_tree_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Bind mouse wheel scrolling
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_tree_frame_configure(self, event):
        """Handle tree frame size changes"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
    
    def _on_canvas_configure(self, event):
        """Handle canvas size changes"""
        # Update the width of the window to fill the canvas
        self.canvas.itemconfig("tree", width=event.width)
    
    def _on_mousewheel(self, event):
        """Handle mousewheel scrolling"""
        # Only scroll if mouse is over the canvas
        if event.widget == self.canvas:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
    
    def _go_to_path(self):
        """Go to the path entered in the path entry"""
        path = self.path_var.get()
        if os.path.exists(path) and os.path.isdir(path):
            self.load_directory(path)
        else:
            # Show error message
            error_label = ctk.CTkLabel(
                self.tree_frame,
                text=f"Invalid path: {path}",
                text_color=get_color("error")
            )
            error_label.pack(padx=10, pady=10)
            
            # Remove error after 3 seconds
            self.after(3000, error_label.destroy)
    
    def _new_file(self):
        """Create a new file in the current directory"""
        # Get current directory
        current_dir = self.path_var.get()
        
        # Create dialog for filename
        dialog = ctk.CTkInputDialog(
            text="Enter new file name:", 
            title="New File"
        )
        filename = dialog.get_input()
        
        if filename:
            # Add .c extension if not specified
            if not os.path.splitext(filename)[1]:
                filename += ".c"
                
            # Create full path
            file_path = os.path.join(current_dir, filename)
            
            try:
                # Check if file exists
                if os.path.exists(file_path):
                    raise FileExistsError(f"File already exists: {filename}")
                
                # Create empty file
                with open(file_path, "w") as f:
                    f.write("""#include <stdio.h>

int main() {
    printf("Hello, World!\\n");
    return 0;
}
""")
                
                # Refresh the view
                self._refresh()
                
                # Open the file
                if "main_panel" in self.state:
                    self.state["main_panel"].tab_view.open_file(file_path)
                
            except Exception as e:
                # Show error
                error_label = ctk.CTkLabel(
                    self.tree_frame,
                    text=f"Error creating file: {str(e)}",
                    text_color=get_color("error")
                )
                error_label.pack(padx=10, pady=10)
                
                # Remove error after 3 seconds
                self.after(3000, error_label.destroy)
    
    def _refresh(self):
        """Refresh the current directory view"""
        self.load_directory(self.path_var.get())
    
    def load_directory(self, path):
        """Load and display a directory structure"""
        # Clear existing tree
        for widget in self.tree_frame.winfo_children():
            widget.destroy()
        
        # Update path
        self.root_path = path
        self.path_var.set(path)
        
        # Check if path exists
        if not os.path.exists(path):
            ctk.CTkLabel(
                self.tree_frame,
                text=f"Path not found: {path}",
                text_color=get_color("error")
            ).pack(padx=10, pady=10)
            return
        
        # Build the file tree
        self.tree_root = self._build_tree(path)
        
        # Display the tree
        self._render_tree()
    
    def _build_tree(self, root_path, max_depth=3):
        """Build a tree representation of the directory structure"""
        root_node = FileTreeNode(root_path, is_dir=True)
        
        # Queue for BFS traversal with depth tracking
        queue = []  # Using a list for the queue
        queue.append((root_node, 0))  # (node, depth)
        
        while queue:
            node_info = queue.pop(0)
            node = node_info[0]
            depth = node_info[1]
            
            # Don't go deeper than max_depth
            if depth > max_depth:
                continue
            
            try:
                # List directory contents
                if node.is_dir and os.path.exists(node.path):
                    items = os.listdir(node.path)
                    
                    # Filter out system files and unwanted directories
                    items = [item for item in items if not item.startswith('.')]
                    
                    for item in items:
                        item_path = os.path.join(node.path, item)
                        is_dir = os.path.isdir(item_path)
                        
                        # Create child node
                        child = FileTreeNode(item_path, is_dir, node)
                        node.add_child(child)
                        
                        # Add directories to queue for further expansion
                        if is_dir:
                            queue.append((child, depth + 1))
            except (PermissionError, FileNotFoundError):
                # Skip directories we can't access
                pass
        
        return root_node
    
    def _render_tree(self):
        """Render the file tree in the UI"""
        if not self.tree_root:
            return
            
        # Set default expansion for root
        self.tree_root.expanded = True
        
        # Start rendering from root
        self._render_node(self.tree_root, self.tree_frame, 0)
    
    def _render_node(self, node, parent_frame, depth):
        """Render a single node and its children if expanded"""
        # Create frame for this node with Xcode-style hover effect
        node_frame = ctk.CTkFrame(parent_frame, fg_color="transparent", corner_radius=4)
        node_frame.pack(fill="x", pady=1, padx=3)
        
        # Add hover effect
        def on_enter(e):
            node_frame.configure(fg_color=get_color("bg_hover"))
        def on_leave(e):
            node_frame.configure(fg_color="transparent")
        
        node_frame.bind("<Enter>", on_enter)
        node_frame.bind("<Leave>", on_leave)
        
        # Indent based on depth (Xcode uses less indentation)
        indent_frame = ctk.CTkFrame(node_frame, width=depth*16, fg_color="transparent")
        indent_frame.pack(side="left")
        
        # Expansion indicator (only for directories) - Xcode style
        if node.is_dir and node.children:
            icon = "▼" if node.expanded else "▶"
            expander = ctk.CTkButton(
                node_frame,
                text=icon,
                width=16,
                height=16,
                fg_color="transparent",
                hover_color=get_color("bg_hover"),
                text_color=get_color("accent_primary"),
                font=("SF Pro", 10),
                command=lambda n=node, nf=node_frame: self._toggle_node(n, nf, depth)
            )
            expander.pack(side="left")
        else:
            # Spacer for alignment
            spacer = ctk.CTkFrame(node_frame, width=16, fg_color="transparent")
            spacer.pack(side="left")
        
        # Icon based on file type - with Xcode style
        icon = self._get_file_icon(node)
        
        # Folder icons in Xcode are blue
        icon_color = get_color("accent_primary") if node.is_dir else get_color("fg_primary")
        
        icon_label = ctk.CTkLabel(
            node_frame, 
            text=icon, 
            width=20,
            text_color=icon_color,
            font=("SF Pro", 12)
        )
        icon_label.pack(side="left")
        
        # Check git status to determine text color
        text_color = get_color("fg_primary")
        if self.git_manager.is_git_repo() and self.show_git_status:
            status_color = self._get_file_status_color(node.path)
            if status_color:
                text_color = status_color
        
        # Node name as clickable label with Xcode style
        node_label = ClickableLabel(
            node_frame,
            text=node.name,
            anchor="w",
            text_color=text_color,
            font=("SF Pro", 11),
            command=lambda n=node: self._on_node_click(n)
        )
        node_label.pack(side="left", fill="x", expand=True, padx=4)
        
        # Make the entire row clickable
        node_frame.bind("<Button-1>", lambda e, n=node: self._on_node_click(n))
        
        # Render children if expanded
        if node.is_dir and node.expanded:
            children_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
            children_frame.pack(fill="x")
            
            for child in node.get_children():
                self._render_node(child, children_frame, depth + 1)
    
    def _toggle_node(self, node, node_frame, depth):
        """Toggle expansion state of a node"""
        # Toggle expanded state
        node.toggle_expanded()
        
        # Get the parent frame of this node
        parent_frame = node_frame.master
        
        # Remove all widgets after this node
        node_idx = parent_frame.winfo_children().index(node_frame)
        for widget in parent_frame.winfo_children()[node_idx+1:]:
            widget.destroy()
        
        # Re-render this node and its children
        self._render_node(node, parent_frame, depth)
    
    def _on_node_click(self, node):
        """Handle node click event"""
        if node.is_dir:
            # For directories, load the directory
            self.load_directory(node.path)
        else:
            # For files, open in editor
            if "main_panel" in self.state:
                self.state["main_panel"].tab_view.open_file(node.path)
    
    def _get_branch_name(self):
        """Get current git branch name"""
        if not self.git_manager.is_git_repo():
            return "No Git Repository"
        
        branch = self.git_manager.get_current_branch()
        if branch:
            return branch
        return "No Branch"
    
    def _refresh_git_status(self):
        """Refresh git status information"""
        # Update the branch name
        self.branch_label.configure(text=self._get_branch_name())
        
        # Show/hide branch frame based on git repo status
        if self.git_manager.is_git_repo():
            self.branch_frame.pack(fill="x", side="top", after=self.canvas)
        else:
            self.branch_frame.pack_forget()
        
        # Refresh the file tree to show git status
        self._refresh()
    
    def _toggle_git_status(self):
        """Toggle display of git status indicators"""
        self.show_git_status = not self.show_git_status
        self._refresh()
    
    def _get_file_status_color(self, node_path):
        """Get color for file based on git status"""
        if not self.git_manager.is_git_repo() or not self.show_git_status:
            return None
        
        # Try to get relative path
        if self.root_path and os.path.isabs(node_path):
            try:
                rel_path = os.path.relpath(node_path, self.root_path)
            except ValueError:
                # File is outside repository
                return None
        else:
            rel_path = node_path
        
        status = self.git_manager.get_file_status(rel_path)
        # Git status codes: M (modified), A (added), D (deleted), ?? (untracked)
        if status == "M" or status == " M":
            return "#e2c08d"  # Yellow-orange color for modified
        elif status == "??" or status == "A" or status == " A":
            return "#81b88b"  # Green color for new/untracked
        elif status == "D" or status == " D":
            return "#f14c4c"  # Red color for deleted
        
        return None
    
    def _get_file_icon(self, node):
        """Get an appropriate icon for a file type"""
        if node.is_dir:
            return "📁"  # Folder icon
            
        # Get file extension
        _, ext = os.path.splitext(node.name)
        ext = ext.lower()
        
        # Map extensions to icons
        icons = {
            ".c": "©️",    # C file
            ".h": "🔤",    # Header file
            ".cpp": "➕",  # C++ file
            ".txt": "📝",  # Text file
            ".md": "📑",   # Markdown
            ".py": "🐍",   # Python
            ".exe": "⚙️",  # Executable
            ".json": "🔠", # JSON
            ".xml": "🔣",  # XML
            ".html": "🌐", # HTML
        }
        
        # Check git status and add indicator
        status_color = self._get_file_status_color(node.path)
        if status_color:
            # If we have git status, we could modify the icon or add a status character
            # but for simplicity, we'll just use the normal icon and color it in the node label
            pass
        
        return icons.get(ext, "📄")  # Default file icon
