#!/usr/bin/env python3
"""
Generate Validation Markdown Documentation

Parses the LinkML schema to extract all validation rules and generates
markdown documentation files for each class that has validations.
"""

import logging
from pathlib import Path
from typing import Dict, List, Set, Any
from utils import load_linkml_schema

# Constants
SCRIPT_DIR = Path(__file__).parent
SCHEMA_PATH = SCRIPT_DIR.parent / "schema" / "TC57CIM-reduced.yml"
DOCS_DIR = SCRIPT_DIR.parent / "docs" / "validations"


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
                                 validations: Dict[str, Dict[str, Any]]) -> str:
    """
    Generate markdown content for a class with validations.
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

    if 'classes' not in schema:
        logging.error("No classes found in schema")
        return

    for class_name, class_data in schema['classes'].items():
        if has_validations(class_data):
            classes_with_validations.append(class_name)

            # Extract validations
            validations = extract_validations(class_data)

            # Generate markdown
            markdown = generate_validation_markdown(class_name, class_data, validations)

            # Write to file
            output_file = DOCS_DIR / f"{class_name}.md"
            output_file.write_text(markdown)

            logging.info(f"Generated: {output_file.name}")

    # Summary
    logging.info("=" * 70)
    logging.info(f"Total classes processed: {len(schema['classes'])}")
    logging.info(f"Classes with validations: {len(classes_with_validations)}")
    logging.info(f"Markdown files generated: {len(classes_with_validations)}")
    logging.info("=" * 70)


if __name__ == "__main__":
    main()
