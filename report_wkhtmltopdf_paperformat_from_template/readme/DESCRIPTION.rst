This is a technical module that allows to force a paperformat directly from the
report QWeb template definition.

This is useful in situations where the report content is dynamically chosen, depending
on some record conditions, and a different paperformat needs to be used for each.

In core, Odoo already allows to overwrite some paperformat values like the ``margin-top``,
``header-spacing``, etc.. through special ``data-report-*`` attributes in the root ``html``
tag of the report QWeb template. This module extends this feature to allow to overwrite
the paperformat itself.
