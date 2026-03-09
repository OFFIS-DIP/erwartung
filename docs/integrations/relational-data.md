---
icon: lucide/database
---

# Relational Databases
You can create both SQL-DDL and SQL-DQL queries. SQL-DDL is used to inintialize a database, SQL-DQL is used to validate your data in the databases. 


## Steps

!!! Note
    Make sure that you have `linkml > 1.11.0` installed.

1. Clone the [repository](github.com/OFFIS-DIP/erwartung) and install the required packages from `pyproject.toml`.
1. To initialize your database, you need SQL-DDL queries (with commands like CREATE etc.). These can be created by running
    ``` sh
    linkml generate sqltables schema/TC57CIM-reduced.yml > tables.sql
    ```

1. To test your database, you need SQL-DQL queries (with commands like SELECT etc.). These can be created by running
    ``` sh
    linkml generate sqlvalidation schema/TC57CIM-reduced.yml > validation.sql
    ```
    Make sure that you have `linkml>1.11.0` installed by running `linkml --version`, otherwise `sqlvalidation` is not part of the software.

1. The default sql dialect is `sqlite`. You can change the dialect with the `--dialect` flag. For more information, check the [linkml documentation](https://linkml.io/linkml/generators/sqlvalidation.html).