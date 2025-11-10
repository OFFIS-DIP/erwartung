---
title: Data Unit Tests
---



Data unit tests are automated checks that validate individual data records against the rules defined in a data model or schema.  
They ensure that each piece of data conforms to expectations such as required fields, value ranges, pattern formats, and conditional logic before the data is used downstream (e.g., in analytics, simulations, or reporting).

In the energy domain, data unit tests can be used to catch common modelling errors.

??? example

    * **PowerTransformer rating** – Verify that a `PowerTransformer` entity has a `BaseVoltage` attribute that falls within a realistic range.
    * **Transmission line length** – Ensure that a transmission line entity’s `length` attribute is a non‑negative decimal.
    * **Meter reading timestamp** – Check that a `MeterReading` time attributes  follows an ISO‑8601 timestamp pattern.

These tests help maintain data quality, reduce downstream errors, and provide early feedback to data producers.

## Categories of data tests
## Required attributes
Attributes can be defined as `required`, meaning that tests fail for entities that do not have these attributes:
```yaml
 Tower:
    is_a: Structure
    slot_usage:
      height:
        required: true
```

## Range of attributes
The range of attributes can be defined. Ranges can either be `types` like `decimal` or `string`, or they can be other classes, or types:
```yaml
Structure:
  attributes:
    height:
      range: decimal
```
LinkML provides more information on [ranges](https://linkml.io/linkml/schemas/slots.html#ranges){target="_blank" rel="noopener noreferrer"}.

## Number values - Upper and lower boundaries
For attributes with a range `decimal` or `integer`, upper and lower boundaries can be set using `maximum_value` and `minimum_value`:
```yaml
 Tower:
    is_a: Structure
    slot_usage:
      height:
        maximum_value: 200
        minimum_value: 0
```
## String values - Regular Expressions
[Regular expressions](https://en.wikipedia.org/wiki/Regular_expression){target="_blank" rel="noopener noreferrer"} can be used to test string values. They are defined as `pattern`:
```yaml
 IdentifiedObject:
    class_uri: cim:IdentifiedObject
    attributes:
      mRID:
        pattern: "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
```

## Rule based testing
All of the above tests can be defined **conditionally**, meaning that they only trigger if some condition is satisfied. In this example, the maximum height check is only triggered if the material is of type `wood`:

```yaml
Tower:
    is_a: Structure
    rules:
      - description: "If a tower is made of wood, its height needs to be smaller than 40m."
        preconditions:
          slot_conditions:
            materialKind:
              equals_string: wood
        postconditions:
          slot_conditions:
            height:
              maximum_value: 40
```
