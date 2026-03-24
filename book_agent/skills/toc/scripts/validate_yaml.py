import yaml

def validate_yaml(yaml_content: str) -> bool:
    """Validate YAML content."""
    if not yaml_content.strip():
        return False
    try:
        yaml.safe_load(yaml_content)
        return True
    except yaml.YAMLError:
        return False