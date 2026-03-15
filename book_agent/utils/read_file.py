import os

def read_file_content(file_path: str) -> str:
    """Read file content from the given file path and return it as a string."""
    if os.path.exists(file_path):
        instruction_text = open(file_path).read()
    else:
        raise FileNotFoundError(f"Instructions file not found at {file_path}")
    return instruction_text