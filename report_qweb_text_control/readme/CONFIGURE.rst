Default Replacement Elements
-----------------------------

The module provides these default replacement elements:

* ``<CR>`` → Carriage return (``\r``)
* ``<LF>`` → Line feed (``\n``)
* ``<CRLF>`` → Windows line ending (``\r\n``)
* ``<TAB>`` → Tab character (``\t``)
* ``<SEMICOLON>`` → Semicolon (``;``)
* ``<SPAN>`` → Removed (empty string)
* ``<DIV>`` → Removed (empty string)

Field Formatting Functions
--------------------------

The module includes these field formatting functions:

* ``A(value, length=None)`` - Alphanumeric: left-aligned, space-padded
* ``N(value, length=None, digits=None, sign=False)`` - Numeric: right-aligned, 
  zero-padded, optional sign at the end
* ``M(value, length=None)`` - Monetary: calls ``N`` with ``digits=2`` and ``sign=True``
* ``T(value, length=None, digits=2)`` - Tax: calls ``N`` with ``digits=2`` and ``sign=False``
* ``D(value, length=8, dtformat="%Y%m%d")`` - Date: formats dates with 
  customizable format, defaults to yyyymmdd
* ``H(value, length=4, dtformat="%H%M")`` - Time: formats times with 
  customizable format, defaults to hhmm
* ``DT(value, length=12, dtformat="%Y%m%d%H%M")`` - Datetime: formats 
  datetime with customizable format, defaults to yyyyMMddhhmm

Post-processing Behavior
------------------------

The module automatically performs the following post-processing on text 
content:

1. Strips whitespace from each line
2. Removes all line breaks from QWeb template structure
3. Removes HTML elements (SPAN, DIV) completely
4. Replaces special elements with their defined characters
5. Returns single-line output with controlled formatting

This ensures clean, consistent text output regardless of QWeb template 
formatting or HTML elements.
