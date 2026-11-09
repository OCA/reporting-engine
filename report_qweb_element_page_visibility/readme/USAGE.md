To use this module, you need to:

This module applies only to reports rendered with wkhtmltopdf. It does not
apply to reports rendered by PaperMuncher, even though they also use QWeb
templates.

In the QWEB `ir.ui.views` used by your report, you can add an element
with css class with any of the classes described above. For example if
you need to improve invoice report header with invoice's number in every
page but first, and sale order report header with order's name in every
page but last, add this code to external_layout_header:

    <t t-if="o._name == 'account.move'">
        <div class="not-first-page">
            <span t-out="o.name"/>
        </div>
    </t>
    <t t-if="o._name == 'sale.order'">
        <div class="not-last-page">
            <span t-out="o.name"/>
        </div>
    </t>
