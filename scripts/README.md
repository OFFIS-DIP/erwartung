Each script together with all relevant data is placed in one folder in the scripts/ folder. Purpose of scripts are for example to enrich the linkml schema with validation rules.

## gen-validation-markdown.py
When running gen-validation-markdown.py, the markdown documents for viewing all created validation cases are created. This is done as follows:

- Parse the schema/TC57CIM-reduced.yml file
- Find all classes that have a validation defined. Too see what validations look like, have a look t docs/unit-tests.md
- For each class that contains at least one validation:
  - Create a new markdown file in docs/validations
    - Title: Name of the class from schema
    - First text: description of the class from schema
    - List all validations for that class