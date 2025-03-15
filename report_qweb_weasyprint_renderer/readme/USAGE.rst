To use this module, you need to set ``qweb_pdf_engine`` to ``weasyprint``::

   <record id="demo_report" model="ir.actions.report">
       <field name="qweb_pdf_engine">weasyprint</field>
   </record>

In your report template, you have multiple possibilities:

1. ``t-call`` the template ``report_qweb_weasyprint_renderer.html_wrapper`` and add your html code inside it. This takes care of defining metadata, includes some of Odoo's standard assets like fonts and fontawesome and defines some helpful classes:

    `header`/`footer`: divs with this class go into the page margin. Put those divs *before* any content

    `page`/`topage`: elements with this class get the current page number (`page`) or the page count (`topage`) prepended

    Note that bootstrap classes are not available, because bootstrap doesn't go well with weasyprint.

2. Generate a complete html tree (starting with `<html>`), this is the most flexible way to use this addon
3. ``t-call`` one of the the existing ``web.internal_layout`` and ``web.external_layout`` - this tries to have similar behavior as wkhtmltopdf reports wrt headers, footers, document style, but isn't well supported as of yet and very slow because this includes a lot of assets that weasyprint doesn't deal with speedily.

Footers are implemented as margin boxes, which are of fixed height. You can edit the header and footer height per report in the WeasyPrint tab.
