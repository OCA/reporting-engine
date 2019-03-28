This module allows you to add new parameters for a paper format which are
then forwarded to wkhtmltopdf command as arguments. To display the arguments
that wkhtmltopdf accepts go to your command line and type 'wkhtmltopdf -H'.

A commonly used parameter in Odoo is *--disable-smart-shrinking*, that will
disable the automatic resizing of the PDF when converting. This is
important when you intend to have a layout that conforms to certain alignment.
It is very common whenever you need to conform the PDF to a predefined
layoyut (e.g. checks, official forms,...).
