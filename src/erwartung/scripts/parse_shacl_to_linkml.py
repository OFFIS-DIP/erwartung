#!/usr/bin/env python3
"""
SHACL to LinkML Numeric Constraints Converter

Parses CGMES SHACL files to extract numeric value range constraints
and adds them to the LinkML schema in slot_usage sections.
"""

import logging
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
import shutil
from erwartung.scripts.utils import load_linkml_schema

from rdflib import Graph, Namespace
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap
from ruamel.yaml.scalarstring import DoubleQuotedScalarString

# Constants
SCRIPT_DIR = Path(__file__).parent
SHACL_DIR = SCRIPT_DIR / "shacl"
SCHEMA_PATH = SCRIPT_DIR.parent / "schema" / "TC57CIM-reduced.yml"
MAX_LINE_LENGTH = 88 # same as black formatter

# RDF Namespaces
SH = Namespace("http://www.w3.org/ns/shacl#")
CIM = Namespace("http://iec.ch/TC57/CIM100#")
XSD = Namespace("http://www.w3.org/2001/XMLSchema#")

# Global statistics
stats = {
    'files_processed': 0,
    'total_constraints_found': 0,
    'unique_constraints': 0,
    'constraints_added': 0,
    'constraints_skipped_existing': 0,
    'constraints_skipped_not_found': 0,
    'min_only': 0,
    'max_only': 0,
    'both_bounds': 0,
    'exclusive_comments': 0
}


@dataclass
class NumericConstraint:
    """Represents a numeric value range constraint from SHACL"""
    class_name: str
    property_name: str
    min_value: Optional[float] = None
    min_exclusive: bool = False
    max_value: Optional[float] = None
    max_exclusive: bool = False
    source_files: Set[str] = field(default_factory=set)

    def key(self) -> Tuple[str, str]:
        """Unique identifier for this constraint"""
        return (self.class_name, self.property_name)

    def merge_with(self, other: 'NumericConstraint') -> None:
        """Merge constraints from multiple files, using most restrictive bounds"""
        if other.min_value is not None:
            if self.min_value is None:
                self.min_value = other.min_value
                self.min_exclusive = other.min_exclusive
            else:
                # Use the larger minimum (most restrictive)
                if other.min_value > self.min_value:
                    self.min_value = other.min_value
                    self.min_exclusive = other.min_exclusive
                elif other.min_value == self.min_value and other.min_exclusive and not self.min_exclusive:
                    # Prefer exclusive if values are equal
                    self.min_exclusive = True

        if other.max_value is not None:
            if self.max_value is None:
                self.max_value = other.max_value
                self.max_exclusive = other.max_exclusive
            else:
                # Use the smaller maximum (most restrictive)
                if other.max_value < self.max_value:
                    self.max_value = other.max_value
                    self.max_exclusive = other.max_exclusive
                elif other.max_value == self.max_value and other.max_exclusive and not self.max_exclusive:
                    # Prefer exclusive if values are equal
                    self.max_exclusive = True

        self.source_files.update(other.source_files)


def setup_logging():
    """Configure logging for the script"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(levelname)s: %(message)s'
    )


def parse_shacl_files() -> Dict[Tuple[str, str], NumericConstraint]:
    """
    Phase 1: Parse all SHACL .ttl files and extract numeric constraints

    Returns:
        Dictionary mapping (class_name, property_name) to NumericConstraint
    """
    logging.info(f"Scanning SHACL directory: {SHACL_DIR}")

    ttl_files = list(SHACL_DIR.glob("*.ttl"))
    logging.info(f"Found {len(ttl_files)} SHACL files to process")

    all_constraints: Dict[Tuple[str, str], NumericConstraint] = {}

    for ttl_file in ttl_files:
        try:
            constraints = parse_single_shacl_file(ttl_file)
            stats['files_processed'] += 1
            stats['total_constraints_found'] += len(constraints)

            # Merge with existing constraints
            for constraint in constraints:
                key = constraint.key()
                if key in all_constraints:
                    all_constraints[key].merge_with(constraint)
                else:
                    all_constraints[key] = constraint

            logging.debug(f"Processed {ttl_file.name}: found {len(constraints)} constraints")

        except Exception as e:
            logging.error(f"Error parsing {ttl_file.name}: {e}")
            continue

    stats['unique_constraints'] = len(all_constraints)
    logging.info(f"Found {stats['total_constraints_found']} total constraints")
    logging.info(f"Deduplicated to {stats['unique_constraints']} unique constraints")

    return all_constraints


def parse_single_shacl_file(ttl_file: Path) -> List[NumericConstraint]:
    """Parse a single SHACL .ttl file and extract numeric constraints"""
    # Read file and fix invalid @# comment syntax
    with open(ttl_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace @# with # at the start of lines (invalid Turtle syntax)
    content = content.replace('@#', '#')

    # Parse the corrected content
    g = Graph()
    g.parse(data=content, format='turtle')

    constraints = []

    # SPARQL query to find all numeric constraints
    query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        PREFIX cim: <http://iec.ch/TC57/CIM100#>

        SELECT ?shape ?path ?minInc ?maxInc ?minExc ?maxExc
        WHERE {
            ?shape a sh:PropertyShape ;
                   sh:path ?path .
            OPTIONAL { ?shape sh:minInclusive ?minInc }
            OPTIONAL { ?shape sh:maxInclusive ?maxInc }
            OPTIONAL { ?shape sh:minExclusive ?minExc }
            OPTIONAL { ?shape sh:maxExclusive ?maxExc }
            FILTER (bound(?minInc) || bound(?maxInc) || bound(?minExc) || bound(?maxExc))
        }
    """

    results = g.query(query)

    for row in results:
        # Parse the sh:path to extract class and property names
        path_str = str(row.path)

        # Expected format: http://iec.ch/TC57/CIM100#ClassName.propertyName
        if '#' not in path_str or '.' not in path_str:
            logging.warning(f"Unexpected sh:path format: {path_str}")
            continue

        # Extract class and property
        after_hash = path_str.split('#')[1]
        if '.' not in after_hash:
            logging.warning(f"No property separator in: {path_str}")
            continue

        class_name, property_name = after_hash.split('.', 1)

        # Extract constraint values
        min_val = None
        min_exc = False
        max_val = None
        max_exc = False

        if row.minInc is not None:
            min_val = float(row.minInc)
            min_exc = False
        elif row.minExc is not None:
            min_val = float(row.minExc)
            min_exc = True

        if row.maxInc is not None:
            max_val = float(row.maxInc)
            max_exc = False
        elif row.maxExc is not None:
            max_val = float(row.maxExc)
            max_exc = True

        # Create constraint object
        constraint = NumericConstraint(
            class_name=class_name,
            property_name=property_name,
            min_value=min_val,
            min_exclusive=min_exc,
            max_value=max_val,
            max_exclusive=max_exc,
            source_files={ttl_file.name}
        )

        constraints.append(constraint)

    return constraints


def merge_constraints(
    constraints: Dict[Tuple[str, str], NumericConstraint],
    schema: CommentedMap,
    test_source_prefix: str = "ENTSOE Application Profiles Library v1.1.0"
) -> CommentedMap:
    """
    Phase 3: Merge SHACL constraints into LinkML schema

    Args:
        constraints: Dictionary of constraints to add
        schema: LinkML schema dictionary

    Returns:
        Updated schema dictionary
    """
    logging.info("Merging constraints into schema...")

    classes = schema['classes']

    for (class_name, property_name), constraint in constraints.items():
        # Check if class exists
        if class_name not in classes:
            logging.warning(f"Class not found in schema: {class_name}")
            stats['constraints_skipped_not_found'] += 1
            continue

        class_def = classes[class_name]

        # Check if property exists in attributes
        if 'attributes' not in class_def or property_name not in class_def['attributes']:
            logging.warning(f"Property not found: {class_name}.{property_name}")
            stats['constraints_skipped_not_found'] += 1
            continue

        # Ensure slot_usage section exists
        if 'slot_usage' not in class_def:
            class_def['slot_usage'] = CommentedMap()

        slot_usage = class_def['slot_usage']

        # Check if property already has constraints defined
        if property_name not in slot_usage:
            slot_usage[property_name] = CommentedMap()

        property_usage = slot_usage[property_name]

        # Merge mode: only add missing constraints
        added_min = False
        added_max = False

        if constraint.min_value is not None:
            property_usage['minimum_value'] = constraint.min_value
            added_min = True

            # Add comment for exclusive bounds
            if constraint.min_exclusive:
                property_usage.yaml_add_eol_comment(
                    'Original SHACL constraint was exclusive (>)',
                    'minimum_value'
                )
                stats['exclusive_comments'] += 1

        if constraint.max_value is not None:
            property_usage['maximum_value'] = constraint.max_value
            added_max = True

            # Add comment for exclusive bounds
            if constraint.max_exclusive:
                property_usage.yaml_add_eol_comment(
                    'Original SHACL constraint was exclusive (<)',
                    'maximum_value'
                )
                stats['exclusive_comments'] += 1

        # Add source information if constraints were added
        if (added_min or added_max) and 'description' not in property_usage:
            # Format source files as a comma-separated list
            description_files = sorted(constraint.source_files)
            description_ref = f"{test_source_prefix} ({', '.join(description_files)})"
            property_usage['description'] = DoubleQuotedScalarString(description_ref)
        # Track statistics
        if added_min or added_max:
            stats['constraints_added'] += 1

            if added_min and added_max:
                stats['both_bounds'] += 1
            elif added_min:
                stats['min_only'] += 1
            else:
                stats['max_only'] += 1
        else:
            stats['constraints_skipped_existing'] += 1

    return schema


def write_updated_schema(schema: CommentedMap, yaml: YAML, schema_path = SCHEMA_PATH) -> None:
    """
    Phase 4: Write updated schema to file with backup

    Args:
        schema: Updated schema dictionary
        yaml: YAML instance for writing
    """
    logging.info("Writing updated schema...")

    # Create backup
    backup_path = schema_path.with_suffix('.yml.backup')
    logging.info(f"Creating backup: {backup_path}")
    shutil.copy2(schema_path, backup_path)

    # Write updated schema
    try:
        with open(schema_path, 'w') as f:
            yaml.dump(schema, f)
        logging.info(f"Successfully wrote updated schema to: {schema_path}")
    except Exception as e:
        logging.error(f"Error writing schema: {e}")
        logging.info(f"Restoring from backup...")
        shutil.copy2(backup_path, schema_path)
        raise


def print_summary():
    """Print summary statistics"""
    print("\n" + "="*60)
    print("SHACL to LinkML Conversion Summary")
    print("="*60)
    print(f"SHACL files processed:           {stats['files_processed']}")
    print(f"Total constraints found:         {stats['total_constraints_found']}")
    print(f"Unique constraints:              {stats['unique_constraints']}")
    print(f"\nConstraints added to schema:     {stats['constraints_added']}")
    print(f"  - Minimum value only:          {stats['min_only']}")
    print(f"  - Maximum value only:          {stats['max_only']}")
    print(f"  - Both min and max:            {stats['both_bounds']}")
    print(f"  - With exclusive comments:     {stats['exclusive_comments']}")
    print(f"\nConstraints skipped:")
    print(f"  - Already exists (merge mode): {stats['constraints_skipped_existing']}")
    print(f"  - Class/property not found:    {stats['constraints_skipped_not_found']}")
    print("="*60)


def main():
    """Main execution function"""
    setup_logging()

    logging.info("Starting SHACL to LinkML conversion...")

    # Phase 1: Parse SHACL files
    constraints = parse_shacl_files()

    # Phase 2: Load LinkML schema
    schema, yaml = load_linkml_schema(schema_path=SCHEMA_PATH)

    # Phase 3: Merge constraints
    schema = merge_constraints(constraints, schema)

    # Phase 4: Write updated schema
    write_updated_schema(schema, yaml)

    # Print summary
    print_summary()

    logging.info("Conversion complete!")


if __name__ == "__main__":
    main()
