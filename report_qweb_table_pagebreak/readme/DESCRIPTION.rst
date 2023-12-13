Control Page Breaks in `<table>`'s within QWeb Reports

The primary objective of this module is to prevent tables
from being split arbitrarily and to provide better control
over page breaks within tables.

This technical module provides developers with a method
to manage page breaks at the table row (`<tr>`) level.

Since `<tr>` elements are not block elements, direct
application of page break properties (`page-break-before`/
`page-break-after` / `page-break-inside`) is not possible.
Instead, this module handles the division of tables and
manages page breaks at the table (`<table>`) level.

**Motivations for Modifying HTML from Python Code:**

Developers may question why HTML is changed from Python code
rather than overloading the report template using QWeb.
Here are the reasons:

1. **Duplicating Table Headers:** Managing report modularity becomes
   challenging when other modules add new columns to tables. This
   solution offers an easy way to maintain overloaded reports
   manipulated by different modules.

2. **Ease of Template Code Writing:** This approach simplifies
   template code by allowing the management of attributes at
   the row level.

.. note::

   Splitting tables happens on QWeb templates so if you share
   templates between your PDF Qweb reports and portails views, it will
   happens on both.
