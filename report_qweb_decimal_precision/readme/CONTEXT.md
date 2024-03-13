Odoo's QWeb reports display values of float fields based on the decimal accuracy
settings, which are global and sometimes bring inconveniences.

For example:

* You have some products which require a fine precision with inventory management (e.g.
  liquid, powder, etc.) and you set 'Product Unit of Measure' to 4, but you don't want
  to show '2.0000 Units' on your quotation to sell assembled products (you may just want
  to show '2 Units').
* You purchase some raw materials in bulk in USD whose unit price comes down to the 4th
  decimal place and you set 'Product Price' to this level or precision, but you don't
  want to show the unit price of a product as '120,000.0000' on your JPY quotation (you
  would just want to show '120,000').

This module is designed to address these inconveniences.
