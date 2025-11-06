# erwartung - what you expect from your energy system data
`erwartung` (pronounced *ɛɐ̯ˈvartʊŋ*, german: expectation) is a collection of data unit tests for the energy domain. It comes with software to export these data unit tests to different formats - ready to be used in your data hub.

Electricity Grid Operators maintain a large amount of data that describes their built assets like power lines, transformer stations, or consumers and producers of electricity. Especially with the idea of having a "Digital Twin" of the grid, the amount of data is rapidly increasing over the last years. To assure high data quality, a lot of data testing needs to be performed. Examples for that are:

* datatypes need to be correct, 
* numerical values need to be within reasonable boundaries (min max values), 
* strings need to convey to regex patterns, 
* quantities of the same assets need to be in reasonable ratios, 
* coordinates need be matching with adresses,
* and many more.
