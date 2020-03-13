# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# Copyright 2019 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from lxml import html

from odoo.tests.common import SavepointCase


class TestAccountInvoiceGroupPicking(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceGroupPicking, cls).setUpClass()
        cls.product = cls.env["product.product"].create(
            {
                "name": "Product for test",
                "default_code": "TESTPROD01",
                "invoice_policy": "delivery",
            }
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Test service product",
                "type": "service",
                "invoice_policy": "order",
            }
        )
        cls.partner = cls.env["res.partner"].create({"name": "Partner for test"})
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.partner.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": cls.product.name,
                            "product_id": cls.product.id,
                            "product_uom_qty": 2,
                            "product_uom": cls.product.uom_id.id,
                            "price_unit": 100.0,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "name": cls.service.name,
                            "product_id": cls.service.id,
                            "product_uom_qty": 3,
                            "product_uom": cls.service.uom_id.id,
                            "price_unit": 50.0,
                        },
                    ),
                ],
            }
        )

    def test_account_invoice_group_picking(self):
        # confirm quotation
        self.sale.action_confirm()
        # deliver lines2
        self.sale.picking_ids[:1].action_confirm()
        self.sale.picking_ids[:1].move_line_ids.write({"qty_done": 1})
        self.sale.picking_ids[:1].action_done()
        # create another sale
        self.sale2 = self.sale.copy()
        self.sale2.order_line[:1].product_uom_qty = 4
        self.sale2.order_line[:1].price_unit = 50.0
        # confirm new quotation
        self.sale2.action_confirm()
        self.sale2.picking_ids[:1].action_confirm()
        self.sale2.picking_ids[:1].move_line_ids.write({"qty_done": 1})
        self.sale2.picking_ids[:1].action_done()
        sales = self.sale | self.sale2
        # invoice sales
        invoice = sales._create_invoices()
        # Test directly grouping method
        # invoice = self.env["account.move"].browse(inv_id)
        groups = invoice.lines_grouped_by_picking()
        self.assertEqual(len(groups), 4)
        self.assertEqual(groups[0]["picking"], groups[1]["picking"])
        self.assertEqual(groups[2]["picking"], groups[3]["picking"])
        # Test report
        content = html.document_fromstring(
            self.env.ref("account.account_invoices").render_qweb_html(invoice.id)[0]
        )
        tbody = content.xpath("//tbody[@class='invoice_tbody']")
        tbody = [html.tostring(line, encoding="utf-8").strip() for line in tbody][
            0
        ].decode()
        # information about sales is printed
        self.assertEqual(tbody.count(self.sale.name), 1)
        self.assertEqual(tbody.count(self.sale2.name), 1)
        # information about pickings is printed
        self.assertTrue(self.sale.invoice_ids.picking_ids[:1].name in tbody)
        self.assertTrue(self.sale2.invoice_ids.picking_ids[:1].name in tbody)

    def test_account_invoice_group_picking_return(self):
        self.sale.action_confirm()
        # deliver lines2
        picking = self.sale.picking_ids[:1]
        picking.action_confirm()
        picking.move_line_ids.write({"qty_done": 1})
        picking.action_done()
        self.sale._create_invoices()
        # Return one picking from sale1
        wiz_return = (
            self.env["stock.return.picking"]
            .with_context(active_model="stock.picking", active_id=picking.id,)
            .create({})
        )
        wiz_return._onchange_picking_id()
        res = wiz_return.create_returns()
        picking_return = self.env["stock.picking"].browse(res["res_id"])
        picking_return.move_line_ids.write({"qty_done": 1})
        picking_return.action_done()
        # Test directly grouping method
        invoice = self.sale._create_invoices(final=True)
        groups = invoice.lines_grouped_by_picking()
        self.assertEqual(len(groups), 1)
        self.assertEqual(groups[0]["picking"], picking_return)
