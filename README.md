# ChiX

ChiX is a Python-based GUI application designed to serve as a C Code Editor and Runner. It provides users with an intuitive interface to write, compile, and run C programs seamlessly. With features like syntax highlighting, file management, and output display, ChiX is ideal for developers and learners working with C.

## Features

- **C Code Editor**: Write and edit C code with syntax highlighting.
- **C Code Runner**: Compile and run C programs directly from the application.
- **File Management**: Create, open, save, and save-as C files within the application.
- **Themed GUI**: Experience a modern dark-theme user interface.

## Installation

To set up ChiX on your local machine, follow these steps:

1. Clone the repository:
   ```bash
   git clone https://github.com/PrakharDoneria/ChiX.git
   cd ChiX
   ```

2. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

3. Ensure you have GCC (MinGW) installed and added to your system's PATH.

## Usage

1. Run the application:
   ```bash
   python app.py
   ```

2. Features available:
   - Write C code in the editor.
   - Use the toolbar to manage files (New, Open, Save, Save As).
   - Compile and run your code using the "Compile & Run" button.

## Code Structure

- **`app.py`**: The main entry point of the application.
- **`core/runner.py`**: Handles code compilation and execution.
- **`utils/highlighter.py`**: Adds syntax highlighting for C code.
- **`compiler/compiler.py`**: Checks GCC installation and compiles C code.
- **`ui/widgets.py`**: Builds the GUI components.
- **`ui/theme.py`**: Configures the application's theme.
- **`core/file_ops.py`**: Manages file operations such as open and save.

## Contributing

Contributions are welcome! Feel free to fork the repository, raise issues, and submit pull requests.

## Acknowledgments

Special thanks to the developers of `customtkinter` and `pygments` for their amazing libraries.