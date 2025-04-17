import subprocess

def check_gcc_installed():
    """Check if gcc (MinGW) is available in PATH."""
    try:
        result = subprocess.run(["gcc", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except FileNotFoundError:
        return False

def compile_c_code(source_path: str, exe_path: str):
    """Compile the C file using gcc and return status and message."""
    compile_cmd = ["gcc", source_path, "-o", exe_path]

    try:
        result = subprocess.run(compile_cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return False, f"[Compilation Error]\n{result.stderr}"
        return True, "[Compilation Successful]\n"
    except Exception as e:
        return False, f"[Error] Failed to compile: {e}"
