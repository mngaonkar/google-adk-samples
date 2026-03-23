import yaml

def validate_yaml(yaml_content: str) -> bool:
    """Validate YAML content."""
    try:
        yaml.safe_load(yaml_content)
        return True
    except yaml.YAMLError:
        return False