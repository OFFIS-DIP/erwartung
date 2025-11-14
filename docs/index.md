---
title: Home
---
# `erwartung` - just what you expect from your energy system data
`erwartung` (pronounced *ɛɐ̯ˈvartʊŋ*, German for “expectation”) is a collection of data unit tests for the energy domain. It includes software that exports these tests to various formats, ready to be used in your data hub.

## Why is this needed?
Electricity grid operators maintain large volumes of data that describe their assets, such as power lines, transformer stations, and electricity consumers and producers. With the rise of “Digital Twin” concepts, the amount of data has been growing rapidly in recent years. To ensure high data quality, data testing is required. Typical concerns include:

- Correct data types  
- Numerical values that fall within reasonable boundaries (minimum and maximum values)  
- Strings that conform to regular‑expression patterns  
- Quantities of similar assets that are in reasonable ratios  
- Coordinates that match physical addresses  
- And many more…





With `erwartung` we do the following: First we formulates generic data tests in a .yml file:

```yaml

WindGeneratingUnit:
    attributes:
        power: 20e6
```



Then, we build software to export these generic tests to the formats that you need in your data platform:

=== "SQL"

    ```sql
    SELECT * FROM "WindGeneratingUnit" WHERE "power" > 20000000;
    ```

=== "SHACL"

    *Generated with LinkML*
    ```yml
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    @prefix sh: <http://www.w3.org/ns/shacl#> .
    @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

    <https://example.org/example/WindGeneratingUnit> a sh:NodeShape ;
        sh:closed true ;
        sh:ignoredProperties ( rdf:type ) ;
        sh:property [ sh:datatype xsd:decimal ;
                sh:maxCount 1 ;
                sh:maxInclusive "20e6" ;
                sh:nodeKind sh:Literal ;
                sh:order 0 ;
                sh:path <https://example.org/example/power> ] ;
        sh:targetClass <https://example.org/example/WindGeneratingUnit> .
    ```

=== "json-schema"

    *Generated with LinkML*
    ```json
    {
        "$defs": {
            "WindGeneratingUnit": {
                "additionalProperties": false,
                "description": "",
                "properties": {
                    "power": {
                        "maximum": "20e6",
                        "type": [
                            "number",
                            "null"
                        ]
                    }
                },
                "title": "WindGeneratingUnit",
                "type": "object"
            }
        },
        "$id": "https://example.org/example",
        "$schema": "https://json-schema.org/draft/2019-09/schema",
        "additionalProperties": true,
        "metamodel_version": "1.7.0",
        "title": "structure_example",
        "type": "object",
        "version": null
    }

    ```

=== "python"

    *Generated with LinkML*
    ```python
    from __future__ import annotations 

    import re
    import sys
    from datetime import (
        date,
        datetime,
        time
    )
    from decimal import Decimal 
    from enum import Enum 
    from typing import (
        Any,
        ClassVar,
        Literal,
        Optional,
        Union
    )

    from pydantic import (
        BaseModel,
        ConfigDict,
        Field,
        RootModel,
        field_validator
    )


    metamodel_version = "None"
    version = "None"


    class ConfiguredBaseModel(BaseModel):
        model_config = ConfigDict(
            validate_assignment = True,
            validate_default = True,
            extra = "forbid",
            arbitrary_types_allowed = True,
            use_enum_values = True,
            strict = False,
        )
        pass




    class LinkMLMeta(RootModel):
        root: dict[str, Any] = {}
        model_config = ConfigDict(frozen=True)

        def __getattr__(self, key:str):
            return getattr(self.root, key)

        def __getitem__(self, key:str):
            return self.root[key]

        def __setitem__(self, key:str, value):
            self.root[key] = value

        def __contains__(self, key:str) -> bool:
            return key in self.root


    linkml_meta = LinkMLMeta({'default_prefix': 'https://example.org/example/',
        'id': 'https://example.org/example',
        'imports': ['linkml:types'],
        'name': 'structure_example',
        'prefixes': {'linkml': {'prefix_prefix': 'linkml',
                                'prefix_reference': 'https://w3id.org/linkml/'}},
        'source_file': 'minimal-example/schema.yml'} )


    class WindGeneratingUnit(ConfiguredBaseModel):
        linkml_meta: ClassVar[LinkMLMeta] = LinkMLMeta({'from_schema': 'https://example.org/example'})

        power: Optional[Decimal] = Field(default=None, le=20000000.0, json_schema_extra = { "linkml_meta": {'alias': 'power', 'domain_of': ['WindGeneratingUnit']} })


    # Model rebuild
    # see https://pydantic-docs.helpmanual.io/usage/models/#rebuilding-a-model
    WindGeneratingUnit.model_rebuild()
    ```


Some intermetdiate text

``` mermaid
flowchart LR
  subgraph Data Unit Tests
  id1@{ shape: docs, label: "📚 Knowledge base of data unit tests" } 
  end
  subgraph Exporters
  id2("SQL Queries")
  id3("Graph‑based data: SHACL") 
  id4("Soon: .yml ")
  id5("...")
  end
  subgraph Integrations
  id2.1("Relational databases")
  id2.2("CSV files with DuckDB 🦆")
  id3.1(".xml and .rdf files")
  id4.1("Data‑pipelining tools: Airflow or dbt")
  id5.1("...")
  end

  id1 --> id2
  id1 --> id3
  id1 --> id4
  id1 --> id5
  id2 --> id2.1
  id2 --> id2.2
  id3 --> id3.1
  id4 --> id4.1
  id5 --> id5.1

  click id1 "unit-tests"
  click id2 "exporters/sql"
  click id3 "exporters/shacl"
```

## Role of LinkML
The Python tool [LinkML](https://linkml.io) serves as the core open‑source library that provides export functionality from a knowledge base (schema file) to various formats. Its capabilities can be extended if additional features are required.