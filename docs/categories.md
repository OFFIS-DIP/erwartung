# Categories of data tests
## Required attributes
Attributes can be defined as `required`, meaning that tests fail for entities that do not have these attributes:
```yaml
 Tower:
    description: "Tower asset. Dimensions of the Tower are specified in associated\
      \ DimensionsInfo class.\r\nWhen used for planning purposes, a transmission tower\
      \ carrying two 3-phase circuits will have 2 instances of Connection, each of\
      \ which will have 3 MountingPoint instances, one for each phase all with coordinates\
      \ relative to a common origin on the tower. (It may also have a 3rd Connection\
      \ with a single MountingPoint for the Neutral line).\r\n"
    from_schema: https://cim.ucaiug.io/ns#TC57CIM.IEC61968.InfIEC61968.InfAssets
    is_a: Structure
    slot_usage:
      height:
        required: true
```

## Range of attributes
The range of attributes can be defined. Ranges can either be `types` like `decimal` or `string`, or they can be other classes, or types:
```yaml
Structure:
  description: "Construction holding assets such as conductors, transformers, switchgear,\
    \ etc. Where applicable, number of conductors can be derived from the number\
    \ of associated wire spacing instances.\r\n"
  attributes:
    height:
      range: decimal
```
LinkML provides more information on [ranges](https://linkml.io/linkml/schemas/slots.html#ranges).

## Number values - Upper and lower boundaries
For attributes with a range `decimal` or `integer`, upper and lower boundaries can be set using `maximum_value` and `minimum_value`:
```yaml
 Tower:
    description: "Tower asset. Dimensions of the Tower are specified in associated\
      \ DimensionsInfo class.\r\nWhen used for planning purposes, a transmission tower\
      \ carrying two 3-phase circuits will have 2 instances of Connection, each of\
      \ which will have 3 MountingPoint instances, one for each phase all with coordinates\
      \ relative to a common origin on the tower. (It may also have a 3rd Connection\
      \ with a single MountingPoint for the Neutral line).\r\n"
    from_schema: https://cim.ucaiug.io/ns#TC57CIM.IEC61968.InfIEC61968.InfAssets
    is_a: Structure
    slot_usage:
      height:
        maximum_value: 200
        minimum_value: 0
```
## String values - Regular Expressions
Regular expressions can be used to test string values. They are defined as `pattern`:
```yaml
 IdentifiedObject:
    class_uri: cim:IdentifiedObject
    tree_root: true
    from_schema: https://cim.ucaiug.io/ns#TC57CIM.IEC61970.Base.Core
    description: This is a root class to provide common identification for all classes
      needing identification and naming attributes.
    attributes:
      mRID:
        pattern: "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
```

## Rule based testing
All of the above tests can be defined conditional, meaning that they only trigger if some condition is satisfied. In this example, the maximum height check is only triggered if the material is of type `wood`:

```yaml
Tower:
    description: "Tower asset. Dimensions of the Tower are specified in associated\
      \ DimensionsInfo class.\r\nWhen used for planning purposes, a transmission tower\
      \ carrying two 3-phase circuits will have 2 instances of Connection, each of\
      \ which will have 3 MountingPoint instances, one for each phase all with coordinates\
      \ relative to a common origin on the tower. (It may also have a 3rd Connection\
      \ with a single MountingPoint for the Neutral line).\r\n"
    from_schema: https://cim.ucaiug.io/ns#TC57CIM.IEC61968.InfIEC61968.InfAssets
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