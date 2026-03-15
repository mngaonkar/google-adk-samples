import os

def read_from_file(file_path: str) -> str:
    """Read file content from the given file path and return it as a string."""
    if os.path.exists(file_path):
        instruction_text = open(file_path).read()
    else:
        raise FileNotFoundError(f"Instructions file not found at {file_path}")
    return instruction_text

def save_to_file(content: str, file_path: str) -> str:
    """
    Save the Table of Contents to a markdown file.
    
    Args:
        content: The table of contents content to save
        file_path: The path to the file where the content will be saved
        
    Returns:
        A confirmation message with the file path
    """
    output_dir = "file_system"
    os.makedirs(output_dir, exist_ok=True)
    
    file_path = f"{output_dir}/table_of_contents.md"
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    return file_path