import os
import logging

logger = logging.getLogger(__name__)

def save_toc_to_file(content: str, file_path: str) -> str:
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
    
    logger.info(f"TOC saved to: {file_path}")
    return f"Table of Contents successfully saved to {file_path}"
