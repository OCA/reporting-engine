Add a new model to define templates of comments to print on
documents. Templates can use jinja instructions.

Two positions are available for the comments:
* above document lines
* below document lines

This module is the base module for following modules:

* sale_comment_template
* purchase_comment_template
* invoice_comment_template
* stock_picking_comment_template

.. note::

  To properly be able to use `${object}` Jinja instructions
  those modules have to forward current record informations.
