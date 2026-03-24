def remove_think_content(content: str) -> str:
    """
    Remove "THINK:" content from the given string.

    Args:
        content: The input string that may contain "<think> </think>" content.

    Returns:
        A string with all "<think> </think>" content removed.
    """
    import re
    # Use regex to remove all occurrences of <think>...</think>
    cleaned_content = content.split("</think>")[1]  # Take content after the first </think>
    return cleaned_content.strip()