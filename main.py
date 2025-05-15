"""
ChiX - Professional VS Code-inspired C Code Editor
Main entry point for the application
"""

import os
import sys

# Ensure the correct working directory
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chix.app import ChiXApp

if __name__ == "__main__":
    # Start the ChiX Editor app in the main thread
    app = ChiXApp()
    app.start()
