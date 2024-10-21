From an imported spreadsheet (xlsx), this module allows to transform file data in 
Polars dataframe and process them according to rules in order to:

- filter data and display 
- obtain another dataframe with only the expected data to use in Odoo

A such dataframe can help to prepare data in order to be used to create/update or import

Typical use case:

You receive files from your vendors and these files have many difference (column names, number of columns, dirty paging) but contains data related to same concepts.
Then you want apply them a common process to automate things.
For that you need to transform/arrange data to the same way


Why dataframe ?

- a dataframe is a kind of in-memory dataset on which you can operate
- you can operates on your entire dataset a bit like with a database but in memory: you don't need to iterate on each line to perform operations
- the operations are powerful: filter, add column resulting from calculation, select a subset of data


Why Polars ?

- performance: code in rust
- environment consideration
- dynamic project
