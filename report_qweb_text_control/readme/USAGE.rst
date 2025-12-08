To create a text-controlled QWeb report, define a report with 
``report_type="qweb-text"`` and enable the "Enable Text Control" option:

.. code-block:: xml

    <record id="action_report_custom_text" model="ir.actions.report">
        <field name="name">Custom Text Report</field>
        <field name="model">your.model</field>
        <field name="report_type">qweb-text</field>
        <field name="text_control_enabled" eval="True"/>
        <field name="report_name">your_module.report_custom_text</field>
        <field name="binding_model_id" ref="model_your_model"/>
        <field name="binding_type">report</field>
    </record>

Special Elements in Templates
------------------------------

In your QWeb template, use special elements for controlled output. HTML elements 
like SPAN and DIV are automatically removed:

.. code-block:: xml

    <template id="report_custom_text">
        <t t-foreach="docs" t-as="doc">
            <span t-esc="doc.name"/>,<span t-esc="doc.email"/><LF/>
            <span t-esc="doc.phone"/>,<span t-esc="doc.address"/><CRLF/>
            <span t-esc="doc.field1"/><TAB/><span t-esc="doc.field2"/><SEMICOLON/><span t-esc="doc.field3"/>
        </t>
    </template>

Field Formatting
-----------------

The module provides field formatting functions available in templates:

.. code-block:: xml

    <!-- Alphanumeric (A): left-aligned, space-padded -->
    <span t-esc="A(doc.name, 10)"/>

    <!-- Numeric (N): right-aligned, zero-padded -->
    <span t-esc="N(doc.amount, 8)"/>

    <!-- Numeric with decimals and sign (sign at the end) -->
    <span t-esc="N(doc.amount, 12, digits=2, sign=True)"/>

    <!-- Monetary (M): calls N with digits=2 and sign=True -->
    <span t-esc="M(doc.total, 12)"/>

    <!-- Date (D): formats dates, defaults to yyyymmdd -->
    <span t-esc="D(doc.date)"/>

    <!-- Date with custom format -->
    <span t-esc="D(doc.date, dtformat='%Y-%m-%d')"/>

    <!-- Date with length padding -->
    <span t-esc="D(doc.date, 12, dtformat='%Y%m%d')"/>

    <!-- Time (T): formats times, defaults to hhmm -->
    <span t-esc="T(doc.time)"/>

    <!-- Time with custom format -->
    <span t-esc="T(doc.time, dtformat='%H:%M')"/>

    <!-- Time with length padding -->
    <span t-esc="T(doc.time, 6, dtformat='%H:%M:%S')"/>

    <!-- Datetime (DT): formats datetime, defaults to yyyyMMddhhmm -->
    <span t-esc="DT(doc.datetime)"/>

    <!-- Datetime with custom format -->
    <span t-esc="DT(doc.datetime, dtformat='%Y-%m-%d %H:%M')"/>

    <!-- Datetime with length padding -->
    <span t-esc="DT(doc.datetime, 20, dtformat='%Y-%m-%d %H:%M:%S')"/>

Customization
-------------

Override the ``_get_replacement_elements()`` method to define your own special 
elements:

.. code-block:: python

    from odoo import models

    class CustomTextReport(models.Model):
        _inherit = "ir.actions.report"
        
        def _get_replacement_elements(self):
            """Override to customize replacement elements"""
            elements = super()._get_replacement_elements()
            elements.update({
                "CUSTOM": "CustomValue",
                "NEWLINE": "\r\n",
            })
            return elements
