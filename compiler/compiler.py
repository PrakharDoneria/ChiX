import subprocess
import os
import shutil

def check_gcc_installed():
    """Check if GCC is installed and available in PATH"""
    try:
        # Try to run gcc --version to check if GCC is installed
        subprocess.run(['gcc', '--version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except FileNotFoundError:
        return False

def compile_c_code(source_path, output_path):
    """Compiles C source code with GCC
    
    Args:
        source_path: Path to .c source file
        output_path: Path to output executable
    
    Returns:
        (success, message): Tuple containing success status and output message
    """
    if not os.path.exists(source_path):
        return False, "[ERROR] Source file not found"
    
    # Delete output file if it already exists
    if os.path.exists(output_path):
        try:
            os.remove(output_path)
        except:
            return False, "[ERROR] Could not remove previous executable"
            
    # Compile the code
    try:
        result = subprocess.run(
            ['gcc', source_path, '-o', output_path], 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Check if compilation was successful
        if result.returncode == 0:
            return True, "[SUCCESS] Compilation completed. Running program..."
        else:
            # Return compilation errors
            error_msg = result.stderr if result.stderr else "Unknown compilation error"
            return False, f"[ERROR] Compilation failed:\n{error_msg}"
            
    except Exception as e:
        return False, f"[ERROR] Compilation process failed: {str(e)}"