The py3o reporting engine is a reporting engine for Odoo based on `Libreoffice <http://www.libreoffice.org/>`_:

* the report is created with Libreoffice (ODT or ODS),
* the report is stored on the server in OpenDocument format (.odt or .ods file)
* the report is sent to the user in OpenDocument format or in any output format supported by Libreoffice (PDF, HTML, DOC, DOCX, Docbook, XLS, etc.)

The key advantages of a Libreoffice based reporting engine are:

* no need to be a developer to create or modify a report: the report is created and modified with Libreoffice. So this reporting engine has a full WYSIWYG report development tool!
* For a PDF report in A4/Letter format, it's easier to develop it with a tool such as Libreoffice that is designed to create A4/Letter documents than to develop it in HTML/CSS, also some print peculiarities (backgrounds, margin boxes) are not very well supported by the HTML/CSS based solutions.
* If you want your users to be able to modify the document after its generation by Odoo, just configure the document with ODT output (or DOC or DOCX) and the user will be able to modify the document with Libreoffice (or Word) after its generation by Odoo.
* Easy development of spreadsheet reports in ODS format (XLS output possible).

This module *report_py3o* is the base module for the Py3o reporting engine. If used alone, it will spawn a libreoffice process for each ODT to PDF (or ODT to DOCX, ..) document conversion. This is slow and can become a problem if you have a lot of reports to convert from ODT to another format. In this case, you should consider the additionnal module *report_py3o_fusion_server* which is designed to work with a libreoffice daemon. With *report_py3o_fusion_server*, the technical environnement is more complex to setup because you have to install additionnal software components and run 2 daemons, but you have much better performances and you can configure the libreoffice PDF export options in Odoo (allows to generate PDF forms, PDF/A documents, password-protected PDFs, watermarked PDFs, etc.).

This reporting engine is an alternative to `Aeroo <https://github.com/aeroo-community/aeroo_reports>`_: these two reporting engines have similar features but their implementation is entirely different. You cannot use aeroo templates as drop in replacement though, you'll have to change a few details.
