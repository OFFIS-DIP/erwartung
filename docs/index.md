---
title: Home
---
# `erwartung` - just what you expect from your energy system data
`erwartung` (pronounced *ɛɐ̯ˈvartʊŋ*, German: expectation) is a collection of data unit tests for the energy domain. It includes software to export these data unit tests to different formats, ready to be used in your data hub.


## Why is this needed?
Electricity Grid Operators maintain a large amount of data that describes their built assets, such as power lines, transformer stations, or electricity consumers and producers. Especially with the concept of a “Digital Twin” of the grid, the amount of data has been rapidly increasing in recent years. To ensure high data quality, extensive testing is required. Examples include:

* data types need to be correct,
* numerical values need to be within reasonable boundaries (minimum and maximum values),
* strings need to conform to regular‑expression patterns,
* quantities of the same assets need to be in reasonable ratios,
* coordinates need to match addresses,
* and many more.


``` mermaid
flowchart LR
  subgraph Data Unit Tests
  id1@{ shape: docs, label: "📚 Knowledge base of data unit tests" } 
  end
  subgraph Exporters
  id2("SQL Queries")
  id3("Graph based data: SHACL") 
  id4("Soon: .yml ")
  id5("...")
  end
  subgraph Integrations
  id2.1("Relational databases")
  id2.2("csv Files with duckDB 🦆")
  id3.1(".xml and .rdf files")
  id4.1("Data Pipelining tools: Airflow or dbt")
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

## Role of linkml
The python tool [linkml](https://linkml.io){target="_blank" rel="noopener noreferrer"} will be used as the basic open source software providing the export functionalities from a Knowledge Base (schema file) to different formats. If needed, the functionality from linkml will be extended.