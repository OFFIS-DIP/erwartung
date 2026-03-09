import logging
from typing import  Tuple

from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

def load_linkml_schema(schema_path, max_line_length=88) -> Tuple[CommentedMap, YAML]:
    """
    Phase 2: Load LinkML schema with ruamel.yaml for round-trip preservation

    Returns:
        Tuple of (schema_dict, yaml_instance)
    """
    logging.info(f"Loading LinkML schema: {schema_path}")

    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")

    # Use ruamel.yaml in round-trip mode
    yaml = YAML()
    yaml.preserve_quotes = True
    yaml.default_flow_style = False
    yaml.width = max_line_length  # Maximum line length before wrapping
    yaml.indent(mapping=2, sequence=2, offset=0)

    with open(schema_path, 'r') as f:
        schema = yaml.load(f)

    if 'classes' not in schema:
        raise ValueError("Schema does not contain 'classes' section")

    num_classes = len(schema['classes'])
    logging.info(f"Loaded schema with {num_classes} classes")

    return schema, yaml
