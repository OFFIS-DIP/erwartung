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
The Python tool [LinkML](https://linkml.io){target="_blank" rel="noopener noreferrer"} serves as the core open‑source library that provides export functionality from a knowledge base (schema file) to various formats. Its capabilities can be extended if additional features are required.