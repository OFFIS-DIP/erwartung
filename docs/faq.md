---
title: Frequently Asked Questions
icon: lucide/circle-question-mark
---


## This can't work, because...

??? question "...grid operators use different data models, right?"
    In `erwartung` we have chosen the **Common Information Model (CIM)** as the core data model for defining the unit tests. This decision is based on two practical considerations:

    * **Broad adoption:** Many grid operators already rely on CIM and its profile CGMES from entso-e to describe parts of their data. This means that for a large number of participants, the data is already in a compatible format, reducing the amount of transformation work required.
    * **Model‑to‑model mappings:** For operators that employ alternative data models, mappings **from CIM to their model** can be defined. These mappings translate the CIM‑based test definitions into the operator’s native schema, allowing the same tests to be executed across heterogeneous systems. Because each operator’s model can differ, a dedicated mapping needs to be developed for every participant. Once the mapping is in place, any updates to the CIM‑based schema in `erwartung` automatically propagate through the mapping layer. We will provide clear guidlines and templates, how these mappings are defined to enable grid operators to independently define their own mappings.

??? question "...data testing is specific for each grid operator?"
    Parts of data testing are indeed specific for each grid operator. However, in the area of built assets, many test cases are generally true and do not depend on the grid operator. These are the test cases that we want to cover at `erwartung`. You can see examples in the [data unit test section](unit-tests.md). 
