The py3o reporting engine is a reporting engine for Odoo based on
\[Libreoffice\](<http://www.libreoffice.org/>):

- the report is created with Libreoffice (ODT or ODS),
- the report is stored on the server in OpenDocument format (.odt or
  .ods file)
- the report is sent to the user in OpenDocument format or in any output
  format supported by Libreoffice (PDF, HTML, DOC, DOCX, Docbook, XLS,
  etc.)

The key advantages of a Libreoffice based reporting engine are:

- no need to be a developer to create or modify a report: the report is
  created and modified with Libreoffice. So this reporting engine has a
  full WYSIWYG report development tool!
- For a PDF report in A4/Letter format, it's easier to develop it with a
  tool such as Libreoffice that is designed to create A4/Letter
  documents than to develop it in HTML/CSS, also some print
  peculiarities (backgrounds, margin boxes) are not very well supported
  by the HTML/CSS based solutions.
- If you want your users to be able to modify the document after its
  generation by Odoo, just configure the document with ODT output (or
  DOC or DOCX) and the user will be able to modify the document with
  Libreoffice (or Word) after its generation by Odoo.
- Easy development of spreadsheet reports in ODS format (XLS output
  possible).

If all the py3o reports are configured to be sent to the user in OpenDocument format (.odt or .ods), LibreOffice is not needed on the Odoo server. If some py3o reports are configured to be sent to the user in PDF, DOCX, XLS or any other non-OpenDocument format, LibreOffice must be installed on the Odoo server.

For the generation of non-OpenDocument formats, the link between this module *report_py3o* and LibreOffice can be setup in 2 different ways:

1. LibreOffice is started and closed upon each py3o report generation. Advantage: easy to setup. Drawback: slow.
2. LibreOffice runs in headless mode in the background and listens on the localhost interface. Advantage: faster. Drawback: a bit more technical to setup.

This reporting engine is an alternative to
\[Aeroo\](<https://github.com/aeroo-community/aeroo_reports>): these two
reporting engines have similar features but their implementation is
entirely different. You cannot use aeroo templates as drop in
replacement though, you'll have to change a few details.
