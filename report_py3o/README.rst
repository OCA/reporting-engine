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

The key advantages of a Libreoffice based reporting engine are:

* no need to be a developer to create or modify a report: the report is created and modified with Libreoffice. So this reporting engine has a full WYSIWYG report development tool!
* For a PDF report in A4/Letter format, it's easier to develop it with a tool such as Libreoffice that is designed to create A4/Letter documents than to develop it in HTML/CSS, also some print peculiarities (backgrounds, margin boxes) are not very well supported by the HTML/CSS based solutions.
* If you want your users to be able to modify the document after its generation by Odoo, just configure the document with ODT output (or DOC or DOCX) and the user will be able to modify the document with Libreoffice (or Word) after its generation by Odoo.
* Easy development of spreadsheet reports in ODS format (XLS output possible).

This reporting engine is an alternative to `Aeroo <https://github.com/aeroo-community/aeroo_reports>`_: these two reporting engines have similar features but their implementation is entirely different. You cannot use aeroo templates as drop in replacement though, you'll have to change a few details.

Installation
============

Install the required python libs:

.. code::

  pip install py3o.template
  pip install py3o.formats

To allow the conversion of ODT or ODS reports to other formats (PDF, DOC, DOCX, etc.), install libreoffice:

.. code::

  apt-get --no-install-recommends install libreoffice

Configuration
=============

For example, to replace the native invoice report by a custom py3o report, add the following XML file in your custom module:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report.xml">
      <field name="report_type">py3o</field>
      <field name="py3o_filetype">odt</field>
      <field name="module">my_custom_module_base</field>
      <field name="py3o_template_fallback">report/account_invoice.odt</field>
  </record>

  </odoo>

where *my_custom_module_base* is the name of the custom Odoo module. In this example, the invoice ODT file is located in *my_custom_module_base/report/account_invoice.odt*.

It's also possible to reference a template located in a trusted path of your
Odoo server. In this case you must let the *module* entry empty and specify
the path to the template as *py3o_template_fallback*.

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report.xml">
      <field name="report_type">py3o</field>
      <field name="py3o_filetype">odt</field>
      <field name="py3o_template_fallback">/odoo/templates/py3o/report/account_invoice.odt</field>
  </record>

  </odoo>

Moreover, you must also modify the Odoo server configuration file to declare
the allowed root directory for your py3o templates. Only templates located
into this directory can be loaded by py3o report.

.. code::

  [options]
  ...

  [report_py3o]
  root_tmpl_path=/odoo/templates/py3o

If you want an invoice in PDF format instead of ODT format, the XML file should look like:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report.xml">
      <field name="report_type">py3o</field>
      <field name="py3o_filetype">pdf</field>
      <field name="module">my_custom_module_base</field>
      <field name="py3o_template_fallback">report/account_invoice.odt</field>
  </record>

  </odoo>

If you want to add a new py3o PDF report (and not replace a native report), the XML file should look like this:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="partner_summary_report" model="ir.actions.report.xml">
      <field name="name">Partner Summary</field>
      <field name="model">res.partner</field>
      <field name="report_name">res.partner.summary</field>
      <field name="report_type">py3o</field>
      <field name="py3o_filetype">pdf</field>
      <field name="module">my_custom_module_base</field>
      <field name="py3o_template_fallback">report/partner_summary.odt</field>
  </record>

  <!-- Add entry in "Print" drop-down list -->
  <record id="button_partner_summary_report" model="ir.values">
      <field name="key2">client_print_multi</field>
      <field name="model">res.partner</field>
      <field name="name">Partner Summary</field>
      <field name="value" eval="'ir.actions.report.xml,%d'%partner_summary_report" />
  </record>

  </odoo>

Configuration parameters
------------------------

py3o.conversion_command
    The command to be used to run the conversion, ``libreoffice`` by default. If you change this, whatever you set here must accept the parameters ``--headless --convert-to $ext $file`` and put the resulting file into ``$file``'s directory with extension ``$ext``. The command will be started in ``$file``'s directory.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/10.0

The templating language is `extensively documented <http://py3otemplate.readthedocs.io/en/latest/templating.html>`_, the records are exposed in libreoffice as ``objects``, on which you can also call functions.

Available functions and objects
-------------------------------

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

Sample report templates
-----------------------

Sample py3o report templates for the main Odoo native reports (invoice, sale order, purchase order, picking, ...) are available on the Github project `odoo-py3o-report-templates <https://github.com/akretion/odoo-py3o-report-templates>`_.

Known issues / Roadmap
======================

* generate barcode ?
* add more detailed example in demo file to showcase features
* add migration guide aeroo -> py3o

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
* Laurent Mignon <laurent.mignon@acsone.eu>,
* Alexis de Lattre <alexis.delattre@akretion.com>,
* Guewen Baconnier <guewen.baconnier@camptocamp.com>
* Omar Castiñeira <omar@comunitea.com>
* Holger Brunn <hbrunn@therp.nl>


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
