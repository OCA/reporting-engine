# Copyright 2017 Carlos Dauden <carlos.dauden@tecnativa.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import SavepointCase
from odoo.exceptions import ValidationError


class TestProductPricelistDirectPrint(SavepointCase):

    @classmethod
    def setUpClass(cls):
        super(TestProductPricelistDirectPrint, cls).setUpClass()
        cls.pricelist = cls.env.ref('product.list0')
        cls.category = cls.env['product.category'].create({
            'name': 'Test category',
            'type': 'normal',
        })
        cls.product = cls.env['product.product'].create({
            'name': 'Product for test',
            'categ_id': cls.category.id,
            'default_code': 'TESTPROD01',
        })
        cls.partner = cls.env['res.partner'].create({
            'name': 'Partner for test',
            'property_product_pricelist': cls.pricelist.id,
            'email': 'test@test.com',
        })
        cls.wiz_obj = cls.env['product.pricelist.print']

    def test_defaults(self):
        wiz = self.wiz_obj.new()
        res = wiz.with_context(
            active_model='product.pricelist',
            active_id=self.pricelist.id,
        ).default_get([])
        self.assertEqual(res['pricelist_id'], self.pricelist.id)
        res = wiz.with_context(
            active_model='product.pricelist.item',
            active_ids=self.pricelist.item_ids.ids,
        ).default_get([])
        self.assertEqual(res['pricelist_id'], self.pricelist.id)
        res = wiz.with_context(
            active_model='res.partner',
            active_id=self.partner.id,
            active_ids=[self.partner.id],
        ).default_get([])
        self.assertEqual(
            res['pricelist_id'], self.partner.property_product_pricelist.id)
        res = wiz.with_context(
            active_model='product.template',
            active_ids=self.product.product_tmpl_id.ids,
        ).default_get([])
        self.assertEqual(
            res['product_tmpl_ids'][0][2], self.product.product_tmpl_id.ids)
        res = wiz.with_context(
            active_model='product.product',
            active_ids=self.product.ids,
        ).default_get([])
        self.assertEqual(
            res['product_ids'][0][2], self.product.ids)
        self.assertTrue(res['show_variants'])
        with self.assertRaises(ValidationError):
            wiz.print_report()
        wiz.show_sale_price = True
        res = wiz.print_report()
        self.assertIn('report_name', res)

    def test_action_pricelist_send_multiple_partner(self):
        partner_2 = self.env['res.partner'].create({
            'name': 'Partner for test 2',
            'property_product_pricelist': self.pricelist.id,
            'email': 'test2@test.com',
        })
        wiz = self.wiz_obj.with_context(
            active_model='res.partner',
            active_ids=[self.partner.id, partner_2.id],
        ).create({})
        wiz.action_pricelist_send()
