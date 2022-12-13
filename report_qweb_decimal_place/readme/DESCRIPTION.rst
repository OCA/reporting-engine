This module intends to provide the base function for currencies to adjust the number of decimal places
for the unit price in QWeb reports.
Installing this module alone does not affect the presentation of existing QWeb reports.
Individual adjustments need to be done in separate modules in a manner similar to the following:

.. code-block:: xml

    <template
        id="report_saleorder_document_inherit"
        inherit_id="sale.report_saleorder_document"
    >
        <xpath expr="//td[@name='td_priceunit']/span" position="replace">
                <t t-set="currency" t-value="doc.currency_id" />
                <t t-set="price_unit" t-value="line.price_unit" />
                <t t-call="report_qweb_decimal_place.price_unit_value_format" />
        </xpath>
    </template>

Background:
~~~~~~~~~~~

Odoo default reports display price unit with the decimal accuracy of product price configuration.
However, globally applying the decimal accuracy setting is sometimes not appropriate under multi-currency settings
where how unit prices should be presented differs depending on the currency.

For example, unit prices in JPY usually do not have decimals (with some exceptions depending on the industry),
while those in USD may require up to 2-4 decimals.  If we configure the decimal accuracy based on USD, the unit price
presentation on PDF reports for JPY transactions may appear  a bit unconventional.
