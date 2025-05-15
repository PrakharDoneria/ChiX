"""
Debugger utilities for ChiX Editor
Provides breakpoint functionality similar to popular IDEs
"""

import tkinter as tk
from chix.ui.theme import get_color

class BreakpointManager:
    """Manages breakpoints in the editor"""
    
    def __init__(self, editor):
        """
        Initialize the breakpoint manager
        
        Args:
            editor: The text editor widget
        """
        self.editor = editor
        self.breakpoints = set()  # Set of line numbers with breakpoints
        self._setup()
    
    def _setup(self):
        """Set up the breakpoint manager"""
        # Create breakpoint tag
        self.editor._textbox.tag_configure(
            "breakpoint", 
            background=get_color("error"),
            foreground="#ffffff"
        )
        
        # Add gutter click handler for breakpoints
        self.editor.bind("<Button-1>", self._handle_gutter_click, add="+")
    
    def _handle_gutter_click(self, event):
        """Handle click in the gutter to toggle breakpoints"""
        # Check if click is in the gutter area (first 30 pixels)
        if event.x < 30:
            # Get line number from click position
            index = self.editor._textbox.index(f"@{event.x},{event.y}")
            line = int(index.split('.')[0])
            self.toggle_breakpoint(line)
            return "break"  # Prevent further handling
    
    def toggle_breakpoint(self, line):
        """
        Toggle a breakpoint at the given line
        
        Args:
            line (int): Line number to toggle breakpoint
        """
        # Check if the breakpoint already exists
        if line in self.breakpoints:
            self.remove_breakpoint(line)
        else:
            self.add_breakpoint(line)
    
    def add_breakpoint(self, line):
        """
        Add a breakpoint at the given line
        
        Args:
            line (int): Line number to add breakpoint
        """
        if line not in self.breakpoints:
            self.breakpoints.add(line)
            # Add visual indicator
            self._update_breakpoint_display(line, True)
            
            # Call custom event handler if defined
            if hasattr(self.editor, "on_breakpoint_added"):
                self.editor.on_breakpoint_added(line)
    
    def remove_breakpoint(self, line):
        """
        Remove a breakpoint from the given line
        
        Args:
            line (int): Line number to remove breakpoint
        """
        if line in self.breakpoints:
            self.breakpoints.remove(line)
            # Remove visual indicator
            self._update_breakpoint_display(line, False)
            
            # Call custom event handler if defined
            if hasattr(self.editor, "on_breakpoint_removed"):
                self.editor.on_breakpoint_removed(line)
    
    def _update_breakpoint_display(self, line, is_active):
        """
        Update the visual display of a breakpoint
        
        Args:
            line (int): Line number of the breakpoint
            is_active (bool): Whether the breakpoint is active
        """
        # Clear any existing breakpoint indicator
        self.editor._textbox.tag_remove("breakpoint", f"{line}.0", f"{line}.end")
        
        # Add new indicator if active
        if is_active:
            # Add dot in gutter
            self._add_breakpoint_marker(line)
            
            # Highlight the line
            self.editor._textbox.tag_add("breakpoint", f"{line}.0", f"{line}.0 lineend")
    
    def _add_breakpoint_marker(self, line):
        """
        Add a breakpoint marker in the gutter
        
        Args:
            line (int): Line number for the marker
        """
        # Using the line numbers as guide, the actual marker is drawn
        # in the editor's update function
        
        # For now, we'll rely on line highlighting only
        # A more complete implementation would add actual markers in the gutter
        pass
    
    def get_breakpoints(self):
        """
        Get all breakpoints
        
        Returns:
            set: Set of line numbers with breakpoints
        """
        return self.breakpoints.copy()
    
    def clear_all_breakpoints(self):
        """Clear all breakpoints"""
        for line in list(self.breakpoints):
            self.remove_breakpoint(line)
    
    def update_after_text_change(self):
        """Update breakpoints after text changes"""
        # Re-apply all breakpoint markers
        for line in self.breakpoints:
            self._update_breakpoint_display(line, True)

class DebuggingSession:
    """Manages a debugging session"""
    
    def __init__(self, editor, breakpoint_manager):
        """
        Initialize a debugging session
        
        Args:
            editor: The text editor widget
            breakpoint_manager: The breakpoint manager
        """
        self.editor = editor
        self.breakpoint_manager = breakpoint_manager
        self.current_line = None
        self.is_running = False
        
        # Create current line execution tag
        self.editor._textbox.tag_configure(
            "debug_current_line", 
            background=get_color("selection"),
            foreground=get_color("fg_primary"),
            borderwidth=1,
            relief="solid"
        )
    
    def start(self):
        """Start a debugging session"""
        self.is_running = True
        # In a real implementation, this would connect to a debugger
        # and start executing the program
        
        # For demo purposes, just highlight the first non-empty line
        for i in range(1, 100):  # Check first 100 lines
            line_text = self.editor._textbox.get(f"{i}.0", f"{i}.end")
            if line_text.strip():
                self.set_current_line(i)
                break
    
    def stop(self):
        """Stop the debugging session"""
        self.is_running = False
        self.clear_current_line()
    
    def step_into(self):
        """Step into the current function"""
        if not self.is_running or self.current_line is None:
            return
            
        # In a real implementation, this would command the debugger
        # to step into a function
        
        # For demo purposes, just move to the next line
        self.set_current_line(self.current_line + 1)
    
    def step_over(self):
        """Step over the current line"""
        if not self.is_running or self.current_line is None:
            return
            
        # In a real implementation, this would command the debugger
        # to step over a function call
        
        # For demo purposes, just move to the next line
        self.set_current_line(self.current_line + 2)
    
    def step_out(self):
        """Step out of the current function"""
        if not self.is_running or self.current_line is None:
            return
            
        # In a real implementation, this would command the debugger
        # to step out of a function
        
        # For demo purposes, just move to a line a few lines away
        self.set_current_line(self.current_line + 5)
    
    def continue_execution(self):
        """Continue execution until the next breakpoint"""
        if not self.is_running or self.current_line is None:
            return
            
        # In a real implementation, this would command the debugger
        # to continue execution until the next breakpoint
        
        # For demo purposes, find the next breakpoint
        breakpoints = sorted(self.breakpoint_manager.get_breakpoints())
        next_bp = None
        
        for bp in breakpoints:
            if bp > self.current_line:
                next_bp = bp
                break
        
        if next_bp:
            self.set_current_line(next_bp)
        else:
            # No more breakpoints, stop debugging
            self.stop()
    
    def set_current_line(self, line):
        """
        Set the current execution line
        
        Args:
            line (int): Line number
        """
        self.clear_current_line()
        self.current_line = line
        
        # Add visual indicator
        self.editor._textbox.tag_add("debug_current_line", f"{line}.0", f"{line}.end")
        
        # Ensure line is visible
        self.editor._textbox.see(f"{line}.0")
    
    def clear_current_line(self):
        """Clear the current execution line indicator"""
        if self.current_line is not None:
            self.editor._textbox.tag_remove("debug_current_line", f"{self.current_line}.0", f"{self.current_line}.end")
            self.current_line = None

def add_debug_toolbar(parent, debugging_session):
    """
    Add a debugging toolbar to the parent widget
    
    Args:
        parent: Parent widget for the toolbar
        debugging_session: Debugging session to control
    
    Returns:
        Frame: The toolbar frame
    """
    import customtkinter as ctk
    
    toolbar = ctk.CTkFrame(parent, fg_color=get_color("bg_secondary"), height=30)
    
    # Start/Stop button
    start_stop_btn = ctk.CTkButton(
        toolbar,
        text="▶",
        width=28,
        height=22,
        corner_radius=4,
        command=lambda: toggle_debug(start_stop_btn, debugging_session)
    )
    start_stop_btn.pack(side="left", padx=5)
    
    # Step into button
    step_into_btn = ctk.CTkButton(
        toolbar,
        text="→",
        width=28,
        height=22,
        corner_radius=4,
        command=debugging_session.step_into
    )
    step_into_btn.pack(side="left", padx=2)
    
    # Step over button
    step_over_btn = ctk.CTkButton(
        toolbar,
        text="↷",
        width=28,
        height=22,
        corner_radius=4,
        command=debugging_session.step_over
    )
    step_over_btn.pack(side="left", padx=2)
    
    # Step out button
    step_out_btn = ctk.CTkButton(
        toolbar,
        text="↱",
        width=28,
        height=22,
        corner_radius=4,
        command=debugging_session.step_out
    )
    step_out_btn.pack(side="left", padx=2)
    
    # Continue button
    continue_btn = ctk.CTkButton(
        toolbar,
        text="⇥",
        width=28,
        height=22,
        corner_radius=4,
        command=debugging_session.continue_execution
    )
    continue_btn.pack(side="left", padx=2)
    
    def toggle_debug(button, debug_session):
        """Toggle debugging session"""
        if not debug_session.is_running:
            button.configure(text="⏹")
            debug_session.start()
        else:
            button.configure(text="▶")
            debug_session.stop()
    
    return toolbar