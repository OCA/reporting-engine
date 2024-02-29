In a report QWeb template, set the ``data_report_paperformat`` variable to the desired
paperformat ``xmlid``.

For example:

.. code-block:: xml

    <template id="report_invoice" inherit_id="account.report_invoice">
        <xpath expr="//t[@t-call='web.html_container']" position="before">
            <t t-set="data_report_paperformat">my_module.paperformat_custom</t>
        </xpath>
    </template>
