.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

===========
Report Py3o
===========

The py3o reporting engine is a reporting engine for Odoo based on `Libreoffice <http://www.libreoffice.org/>`_:

* the report is created with Libreoffice (ODT or ODS),
* the report is stored on the server in OpenDocument format (.odt or .ods file)
* the report is sent to the user in OpenDocument format or in any output format supported by Libreoffice (PDF, HTML, DOC, DOCX, Docbook, XLS, etc.)

The key advantages of a Libreoffice-based reporting engine are:

* no need to be a developper to create or modify a report: the report is created and modified with Libreoffice. So this reporting engine has a fully WYSIWYG report developpment tool!

* For a PDF report in A4/Letter format, it's easier to develop it with a tool such as Libreoffice that is designed to create A4/Letter documents than to develop it in HTML/CSS.

* If you want your users to be able to modify the document after its generation by Odoo, just configure the document with ODT output (or DOC or DOCX) and the user will be able to modify the document with Libreoffice (or Word) after its generation by Odoo.

* Easy development of spreadsheet reports in ODS format (XLS output possible).

This reporting engine is an alternative to `Aeroo <https://github.com/aeroo/aeroo_reports>`_: these 2 reporting engines have similar features but their codes are completely different.

Installation
============

You must install 2 additionnal python libs:

.. code::

  pip install py3o.template
  pip install py3o.formats

If you want to convert the ODT or ODS report in another format, you need several additionnal components and Python libs:

* `Py3o Fusion server <https://bitbucket.org/faide/py3o.fusion>`_
* `Py3o render server <https://bitbucket.org/faide/py3o.renderserver>`_
* Libreoffice started in the background in headless mode.

TODO : continue

Configuration
=============

If you want to convert the report in another format, go to the menu *Configuration > Technical > Reports > Py3o > Py3o Servers* and create a new Py3o server with its URL (for example:  http://localhost:8765/form).

TODO: continue

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/9.0

Known issues / Roadmap
======================

* generate barcode ?

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Florent Aide (`XCG Consulting <http://odoo.consulting/>`_)
* Laurent Mignon (Acsone)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
