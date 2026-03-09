---
icon: lucide/worm
---


# Python

The schema can be exported to data classes, either by using [python data classes](https://linkml.io/linkml/generators/python.html) or [pydantic](https://linkml.io/linkml/generators/pydantic.html). Pandas dataframes can be tested using the  [pandera generator](https://linkml.io/linkml/generators/pandera.html).

## Steps
1. Clone the [repository](github.com/OFFIS-DIP/erwartung) and install the required packages from `pyproject.toml`.
1. Run 

``` sh
linkml generate python schema/TC57CIM-reduced.yml > orm.py
```