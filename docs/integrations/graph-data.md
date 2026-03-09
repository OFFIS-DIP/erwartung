---
icon: lucide/workflow
---

# Shapes Constraint Language (SHACL) 

Graph data can be tested using the SHACL. [SHACL](https://en.wikipedia.org/wiki/SHACL) is a language to define constraints for graph data. The [linkml Shacl Exporter](https://linkml.io/linkml/generators/shacl.html) can export the data tests from the schema files to SHACL files. With the help of tools like [pyshacl](https://github.com/RDFLib/pySHACL), file formats like `xml` can be tested.

## Steps
1. Clone the [repository](github.com/OFFIS-DIP/erwartung) and install the required packages from `pyproject.toml`.
1. Run 

``` sh
linkml generate shacl schema/TC57CIM-reduced.yml > shacl.ttl
```