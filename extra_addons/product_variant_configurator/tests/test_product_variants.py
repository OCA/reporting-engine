# © 2016 Oihane Crucelaegui - AvanzOSC
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3.0.html

from odoo.tests.common import TransactionCase


class TestProductVariant(TransactionCase):

    def setUp(self):
        super(TestProductVariant, self).setUp()
        self.tmpl_model = self.env['product.template'].with_context(
            check_variant_creation=True)
        self.categ_model = self.env['product.category']
        self.categ1 = self.categ_model.create({
            'name': 'No create variants category',
        })
        self.categ2 = self.categ_model.create({
            'name': 'Create variants category',
            'no_create_variants': False,
        })
        self.attribute = self.env['product.attribute'].create({
            'name': 'Test Attribute',
        })
        self.value1 = self.env['product.attribute.value'].create({
            'name': 'Value 1',
            'attribute_id': self.attribute.id,
        })
        self.value2 = self.env['product.attribute.value'].create({
            'name': 'Value 2',
            'attribute_id': self.attribute.id,
        })

    def test_no_create_variants(self):
        tmpl = self.tmpl_model.create({
            'name': 'No create variants template',
            'no_create_variants': 'yes',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertEqual(len(tmpl.product_variant_ids), 0)
        tmpl = self.tmpl_model.create({
            'name': 'No variants template',
            'no_create_variants': 'yes',
        })
        self.assertEqual(len(tmpl.product_variant_ids), 0)

    def test_no_create_variants_category(self):
        self.assertTrue(self.categ1.no_create_variants)
        tmpl = self.tmpl_model.create({
            'name': 'Category option template',
            'categ_id': self.categ1.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEqual(len(tmpl.product_variant_ids), 0)
        tmpl = self.tmpl_model.create({
            'name': 'No variants template',
            'categ_id': self.categ1.id,
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEqual(len(tmpl.product_variant_ids), 0)

    def test_create_variants(self):
        tmpl = self.tmpl_model.create({
            'name': 'Create variants template',
            'no_create_variants': 'no',
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertEqual(len(tmpl.product_variant_ids), 2)
        tmpl = self.tmpl_model.create({
            'name': 'No variants template',
            'no_create_variants': 'no',
        })
        self.assertEqual(len(tmpl.product_variant_ids), 1)

    def test_create_variants_category(self):
        self.assertFalse(self.categ2.no_create_variants)
        tmpl = self.tmpl_model.create({
            'name': 'Category option template',
            'categ_id': self.categ2.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEqual(len(tmpl.product_variant_ids), 2)
        tmpl = self.tmpl_model.create({
            'name': 'No variants template',
            'categ_id': self.categ2.id,
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEqual(len(tmpl.product_variant_ids), 1)

    def test_category_change(self):
        self.assertTrue(self.categ1.no_create_variants)
        tmpl = self.tmpl_model.create({
            'name': 'Category option template',
            'categ_id': self.categ1.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': self.attribute.id,
                        'value_ids': [(6, 0, [self.value1.id,
                                              self.value2.id])]})],
        })
        self.assertTrue(tmpl.no_create_variants == 'empty')
        self.assertEqual(len(tmpl.product_variant_ids), 0)
        self.categ1.no_create_variants = False
        self.assertEqual(len(tmpl.product_variant_ids), 2)
