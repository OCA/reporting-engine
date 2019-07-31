For example, to replace the native invoice report by a custom py3o report, add the following XML file in your custom module:

.. code::

  <?xml version="1.0" encoding="utf-8"?>
  <odoo>

  <record id="account.account_invoices" model="ir.actions.report">
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

  <record id="account.account_invoices" model="ir.actions.report">
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

  <record id="account.account_invoices" model="ir.actions.report">
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

  <record id="partner_summary_report" model="ir.actions.report">
      <field name="name">Partner Summary</field>
      <field name="model">res.partner</field>
      <field name="report_name">res.partner.summary</field>
      <field name="report_type">py3o</field>
      <field name="py3o_filetype">pdf</field>
      <field name="module">my_custom_module_base</field>
      <field name="py3o_template_fallback">report/partner_summary.odt</field>
      <!-- Add entry in "Print" drop-down list -->
      <field name="binding_type">report</field>
      <field name="binding_model_id" ref="base.model_res_partner"/>
  </record>

  </odoo>

Configuration parameters
~~~~~~~~~~~~~~~~~~~~~~~~

py3o.conversion_command
    The command to be used to run the conversion, ``libreoffice`` by default. If you change this, whatever you set here must accept the parameters ``--headless --convert-to $ext $file`` and put the resulting file into ``$file``'s directory with extension ``$ext``. The command will be started in ``$file``'s directory.
