# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# Copyright 2018 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase
from lxml import html


class TestAccountInvoiceGroupPicking(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestAccountInvoiceGroupPicking, cls).setUpClass()
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'default_code': 'TESTPROD01',
            'invoice_policy': 'delivery',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner for test',
        })
        cls.sale = cls.env['sale.order'].create({
            'partner_id': cls.partner.id,
            'order_line': [
                (0, 0, {
                    'name': cls.product.name,
                    'product_id': cls.product.id,
                    'product_uom_qty': 2,
                    'product_uom': cls.product.uom_id.id,
                    'price_unit': 100.0,
                })]
        })

    def test_account_invoice_group_picking(self):
        # confirm quotation
        self.sale.action_confirm()
        # deliver lines2
        self.sale.picking_ids[:1].force_assign()
        self.sale.picking_ids[:1].move_line_ids.write({'qty_done': 1})
        self.sale.picking_ids[:1].action_done()
        # create another sale
        self.sale2 = self.sale.copy()
        self.sale2.order_line[:1].product_uom_qty = 4
        self.sale2.order_line[:1].price_unit = 50.0
        # confirm new quotation
        self.sale2.action_confirm()
        self.sale2.picking_ids[:1].force_assign()
        self.sale2.picking_ids[:1].move_line_ids.write({'qty_done': 1})
        self.sale2.picking_ids[:1].action_done()
        sales = self.sale | self.sale2
        # invoice sales
        inv_id = sales.action_invoice_create()
        content = html.document_fromstring(
            self.env.ref('account.account_invoices').render_qweb_html(
                inv_id)[0]
        )
        tbody = content.xpath("//tbody[@class='invoice_tbody']")
        tbody = [html.tostring(line, encoding='utf-8').strip()
                 for line in tbody][0].decode()
        # information about sales is printed
        self.assertEqual(tbody.count(self.sale.name), 2)
        self.assertEqual(tbody.count(self.sale2.name), 2)
        # information about pickings is printed
        self.assertTrue(self.sale.invoice_ids.picking_ids[:1].name in tbody)
        self.assertTrue(self.sale2.invoice_ids.picking_ids[:1].name in tbody)
