To use this module, you need to:

In the QWEB ``ir.ui.views`` used by your report,
you can add an element with css class with any of the classes described above.
For example if you need to improve invoice report header with
invoice's number in every page but first, and sale order report header
with order's name in every page but last, add this code to external_layout_header::

    <t t-if="o._table=='account_invoice'">
        <div class="not-first-page">
            <span t-esc="o.number"/>
        </div>
    </t>
    <t t-if="o._table=='sale_order'">
        <div class="not-last-page">
            <span t-esc="o.name"/>
        </div>
    </t>
