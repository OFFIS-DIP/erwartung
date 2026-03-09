#!/usr/bin/env python3
"""
Generate Validation Markdown Documentation

Parses the LinkML schema to extract all validation rules and generates
markdown documentation files for each class that has validations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Any
from collections import defaultdict
from utils import load_linkml_schema

# Constants
SCRIPT_DIR = Path(__file__).parent
SCHEMA_PATH = SCRIPT_DIR.parent / "schema" / "TC57CIM-reduced.yml"
DOCS_DIR = SCRIPT_DIR.parent / "docs" / "validations"
TOML_PATH = SCRIPT_DIR.parent / "zensical.toml"


def setup_logging():
    """Configure logging for the script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )


def has_validations(class_data: Dict[str, Any]) -> bool:
    """
    Check if a class has any validations defined.

    Validations can be in:
    - slot_usage section (with properties like maximum_value, minimum_value, pattern, etc.)
    - attributes section (with validation properties)
    - rules section

    Note: 'required' is not considered a validation.
    """
    # Check for slot_usage validations
    if 'slot_usage' in class_data:
        for attr_name, attr_data in class_data['slot_usage'].items():
            if isinstance(attr_data, dict):
                # Check for validation properties (excluding 'required')
                validation_props = {'maximum_value', 'minimum_value',
                                  'pattern', 'equals_string', 'equals_number'}
                if any(prop in attr_data for prop in validation_props):
                    return True

    # Check for rules
    if 'rules' in class_data:
        return True

    # Check for validations in attributes section
    if 'attributes' in class_data:
        for attr_name, attr_data in class_data['attributes'].items():
            if isinstance(attr_data, dict):
                # Check for validation properties (excluding 'required')
                validation_props = {'maximum_value', 'minimum_value',
                                  'pattern', 'equals_string', 'equals_number'}
                if any(prop in attr_data for prop in validation_props):
                    return True

    return False


def get_first_subclass_after_identified_object(class_name: str,
                                                 schema: Dict[str, Any]) -> str:
    """
    Find the first subclass after IdentifiedObject in the class hierarchy.

    Traverses the class hierarchy from the given class up to IdentifiedObject,
    and returns the direct child of IdentifiedObject in the chain.

    Args:
        class_name: Name of the class to start from
        schema: The full schema containing all classes

    Returns:
        The name of the first subclass after IdentifiedObject, or the class_name
        itself if it directly inherits from IdentifiedObject
    """
    # Build the hierarchy chain from class to IdentifiedObject
    hierarchy = []
    current = class_name

    while current in schema['classes']:
        hierarchy.append(current)
        class_data = schema['classes'][current]

        if 'is_a' in class_data:
            parent = class_data['is_a']
            if parent == 'IdentifiedObject':
                # Current class is a direct child of IdentifiedObject
                return current
            current = parent
        else:
            # No parent, we've reached the top
            break

    # If we got here without finding IdentifiedObject, return the class itself
    return class_name


def get_attribute_description(attr_name: str, class_data: Dict[str, Any],
                              schema: Dict[str, Any]) -> str:
    """
    Get the description for an attribute, searching the class hierarchy.

    Searches in the following order:
    1. Current class's attributes section
    2. Parent class's attributes section (recursively)

    Args:
        attr_name: Name of the attribute
        class_data: The class definition
        schema: The full schema containing all classes

    Returns:
        The attribute description, or empty string if not found
    """
    # First, check the current class's attributes
    if 'attributes' in class_data:
        if attr_name in class_data['attributes']:
            attr_data = class_data['attributes'][attr_name]
            if isinstance(attr_data, dict) and 'description' in attr_data:
                return attr_data['description'].strip()

    # If not found and class has a parent, check the parent recursively
    if 'is_a' in class_data:
        parent_name = class_data['is_a']
        if 'classes' in schema and parent_name in schema['classes']:
            parent_class = schema['classes'][parent_name]
            return get_attribute_description(attr_name, parent_class, schema)

    return ""


def extract_validations(class_data: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    """
    Extract all validations for a class, organized by attribute.

    Returns a dict mapping attribute names to their validation properties.
    Note: 'required' is not considered a validation and is excluded.
    """
    validations = {}

    # Extract from slot_usage
    if 'slot_usage' in class_data:
        for attr_name, attr_data in class_data['slot_usage'].items():
            if isinstance(attr_data, dict):
                validations[attr_name] = dict(attr_data)

    # Extract from attributes with validation properties
    if 'attributes' in class_data:
        for attr_name, attr_data in class_data['attributes'].items():
            if isinstance(attr_data, dict):
                validation_props = {}

                # Check for validation properties
                for prop in ['maximum_value', 'minimum_value', 'pattern',
                           'equals_string', 'equals_number']:
                    if prop in attr_data:
                        validation_props[prop] = attr_data[prop]

                if validation_props:
                    # Merge with existing validations for this attribute
                    if attr_name in validations:
                        validations[attr_name].update(validation_props)
                    else:
                        validations[attr_name] = validation_props

    # Extract rules (if any)
    if 'rules' in class_data:
        validations['_rules'] = class_data['rules']

    return validations


def format_validation_value(value: Any) -> str:
    """Format a validation value for markdown output."""
    if isinstance(value, str):
        # For strings, wrap in quotes if they look like patterns or special values
        if value.startswith('^') or '\\' in value:
            return f'`{value}`'
        return value
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, bool):
        return 'true' if value else 'false'
    else:
        return str(value)


def generate_validation_markdown(class_name: str, class_data: Dict[str, Any],
                                 validations: Dict[str, Dict[str, Any]],
                                 schema: Dict[str, Any]) -> str:
    """
    Generate markdown content for a class with validations.

    Args:
        class_name: Name of the class
        class_data: The class definition
        validations: Extracted validations for the class
        schema: The full schema (needed to look up inherited descriptions)
    """
    lines = []

    # Title
    lines.append(f"# {class_name}")

    # Class URI
    if 'class_uri' in class_data:
        lines.append(class_data['class_uri'])

    lines.append("")

    # Description
    if 'description' in class_data:
        description = class_data['description'].strip()
        lines.append(description)
        lines.append("")

    # Parent class
    if 'is_a' in class_data:
        lines.append(f"*Inherits from: {class_data['is_a']}*")
        lines.append("")

    # Validations section
    lines.append("## Validations")
    lines.append("")

    # Separate rules from attribute validations
    rules = validations.pop('_rules', None)

    # Attribute validations
    if validations:
        for attr_name in sorted(validations.keys()):
            attr_validations = validations[attr_name]
            lines.append(f"### {attr_name}")
            lines.append("")

            # Add attribute description if available
            description = get_attribute_description(attr_name, class_data, schema)
            if description:
                lines.append(description)
                lines.append("")

            for prop, value in sorted(attr_validations.items()):
                # Skip non-validation properties and 'required'
                if prop in ['source', 'slot_uri', 'range', 'multivalued',
                          'description', 'unit', 'required']:
                    continue

                # Format the validation rule
                formatted_value = format_validation_value(value)

                # Use readable names
                prop_name = prop.replace('_', ' ').title()
                lines.append(f"- **{prop_name}**: {formatted_value}")

                # Add source if available
                if 'source' in attr_validations:
                    source = attr_validations['source'].strip()
                    lines.append(f"  - *Source: {source}*")

            lines.append("")

    # Rules-based validations
    if rules:
        lines.append("### Conditional Rules")
        lines.append("")

        for i, rule in enumerate(rules, 1):
            if 'description' in rule:
                lines.append(f"**Rule {i}**: {rule['description']}")
                lines.append("")

            if 'preconditions' in rule:
                lines.append("*Preconditions:*")
                # Format preconditions
                lines.append("```yaml")
                import yaml
                lines.append(yaml.dump(rule['preconditions'], default_flow_style=False).strip())
                lines.append("```")
                lines.append("")

            if 'postconditions' in rule:
                lines.append("*Postconditions:*")
                # Format postconditions
                lines.append("```yaml")
                import yaml
                lines.append(yaml.dump(rule['postconditions'], default_flow_style=False).strip())
                lines.append("```")
                lines.append("")

    return "\n".join(lines)


def update_zensical_toml(classes_by_subclass: Dict[str, List[str]]):
    """
    Update the zensical.toml file with validation navigation structure.

    Args:
        classes_by_subclass: Dict mapping first subclass names to lists of class names
    """
    # Read the existing TOML file
    with open(TOML_PATH, 'r') as f:
        lines = f.readlines()

    # Build the new validations structure
    validations_lines = []
    validations_lines.append('        "unit-tests.md"')

    for subclass in sorted(classes_by_subclass.keys()):
        class_files = sorted(classes_by_subclass[subclass])
        md_paths = ', '.join([f'"validations/{cls}.md"' for cls in class_files])
        validations_lines.append(f'        {{"{subclass}" = [{md_paths}]}}')

    # Create the new validations entry
    new_validations = ',\n'.join(validations_lines)
    new_validations_section = f'    {{"Data Unit Tests" = [\n{new_validations}\n    ]}},\n'

    # Find and replace content between comment markers
    output_lines = []
    i = 0
    start_marker = '# GENERATED BY scripts/gen-validation-markdown.md (Do not alter this line)'
    end_marker = '# END (Do not alter this line)'

    while i < len(lines):
        line = lines[i]

        # Check if this is the start marker
        if start_marker in line:
            # Keep the start marker line
            output_lines.append(line)
            i += 1

            # Skip all lines until we find the end marker
            while i < len(lines):
                if end_marker in lines[i]:
                    # Insert the new validations section before the end marker
                    output_lines.append(new_validations_section)
                    # Keep the end marker line
                    output_lines.append(lines[i])
                    i += 1
                    break
                i += 1
        else:
            # Not a marker line, keep it as-is
            output_lines.append(line)
            i += 1

    # Write the updated TOML file
    with open(TOML_PATH, 'w') as f:
        f.writelines(output_lines)

    logging.info(f"Updated {TOML_PATH} with {len(classes_by_subclass)} validation categories")


def main():
    """Main execution function"""
    setup_logging()

    logging.info("=" * 70)
    logging.info("Generating Validation Markdown Documentation")
    logging.info("=" * 70)

    # Load schema
    schema, _ = load_linkml_schema(SCHEMA_PATH)

    # Ensure output directory exists
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    logging.info(f"Output directory: {DOCS_DIR}")

    # Process all classes
    classes_with_validations = []
    classes_by_subclass = defaultdict(list)

    if 'classes' not in schema:
        logging.error("No classes found in schema")
        return

    for class_name, class_data in schema['classes'].items():
        if has_validations(class_data):
            classes_with_validations.append(class_name)

            # Extract validations
            validations = extract_validations(class_data)

            # Generate markdown (pass schema for inherited descriptions)
            markdown = generate_validation_markdown(class_name, class_data, validations, schema)

            # Write to file
            output_file = DOCS_DIR / f"{class_name}.md"
            output_file.write_text(markdown)

            logging.info(f"Generated: {output_file.name}")

            # Group by first subclass after IdentifiedObject
            first_subclass = get_first_subclass_after_identified_object(class_name, schema)
            classes_by_subclass[first_subclass].append(class_name)

    # Update zensical.toml with validation navigation
    if classes_by_subclass:
        update_zensical_toml(classes_by_subclass)

    # Summary
    logging.info("=" * 70)
    logging.info(f"Total classes processed: {len(schema['classes'])}")
    logging.info(f"Classes with validations: {len(classes_with_validations)}")
    logging.info(f"Markdown files generated: {len(classes_with_validations)}")
    logging.info(f"Validation categories: {len(classes_by_subclass)}")
    logging.info("=" * 70)


if __name__ == "__main__":
    main()
