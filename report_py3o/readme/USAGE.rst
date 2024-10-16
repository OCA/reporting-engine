The templating language is `extensively documented <http://py3otemplate.readthedocs.io/en/latest/templating.html>`_, the records are exposed in libreoffice as ``objects``, on which you can also call functions.

Available functions and objects
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

user
    Browse record of current user
lang
    The user's company's language as string (ISO code)
b64decode
    ``base64.b64decode``
format_multiline_value(string)
    Generate the ODF equivalent of ``<br/>`` and ``&nbsp;`` for multiline fields (ODF is XML internally, so those would be skipped otherwise)
html_sanitize(string)
    Sanitize HTML string
time
    Python's ``time`` module
display_address(partner)
    Return a formatted string of the partner's address
o_format_lang(value, lang_code=False, digits=None, grouping=True, monetary=False, dp=False, currency_obj=False, no_break_space=True)
    Return a formatted numeric or monetary value according to the context language and timezone
o_format_date(value, lang_code=False, date_format=False)
    Return a formatted date or time value according to the context language and timezone


Sample report templates
~~~~~~~~~~~~~~~~~~~~~~~

Sample py3o report templates for the main Odoo native reports (invoice, sale order, purchase order, picking, etc.) are available on the Github project `odoo-py3o-report-templates <https://github.com/akretion/odoo-py3o-report-templates>`_.
