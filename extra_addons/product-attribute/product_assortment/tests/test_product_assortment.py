# Copyright 2018-2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestProductAssortment(TransactionCase):

    def setUp(self):
        super(TestProductAssortment, self).setUp()
        self.filter_obj = self.env['ir.filters']
        self.product_obj = self.env['product.product']
        self.assortment = self.filter_obj.create({
            'name': 'Test Assortment',
            'model_id': 'product.product',
            'is_assortment': True,
            'domain': [],
        })

    def test_assortment(self):
        products = self.product_obj.search([])
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertEqual(products.ids, products_filtered.ids)

        # reduce assortment to services products
        domain = [('type', '=', 'service')]
        self.assortment.domain = domain

        products = self.product_obj.search(domain)
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertEqual(products.ids, products_filtered.ids)

        # include one product not in initial filter
        included_product = self.env.ref('product.product_product_7')
        self.assortment.write({
            'whitelist_product_ids': [(4, included_product.id)]})
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertIn(included_product.id, products_filtered.ids)

        # exclude one product not in initial filter
        excluded_product = self.env.ref('product.product_product_2')
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertIn(excluded_product.id, products_filtered.ids)
        self.assortment.write({
            'blacklist_product_ids': [(4, excluded_product.id)]})
        domain = self.assortment._get_eval_domain()
        products_filtered = self.product_obj.search(domain)
        self.assertNotIn(excluded_product.id, products_filtered.ids)

    def test_assortment_not_available_search_view(self):
        model = self.env.ref('product.model_product_product')
        filters = self.filter_obj.get_filters(model.id)
        self.assertFalse(filters)

    def test_create_assortment_with_context(self):
        assortment = self.filter_obj.with_context(
            product_assortment=True).create({
                'name': 'Test Assortment Context',
                'domain': []})
        self.assertTrue(assortment.is_assortment)
        self.assertEqual(assortment.model_id, 'product.product')
