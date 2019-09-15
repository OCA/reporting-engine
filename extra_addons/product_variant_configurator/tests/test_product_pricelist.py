# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import SavepointCase


class TestProductPriceList(SavepointCase):
    @classmethod
    def setUpClass(cls):
        super(TestProductPriceList, cls).setUpClass()

        # ENVIRONMENTS
        cls.product_template = cls.env['product.template'].with_context(
            check_variant_creation=True)
        cls.product_pricelist = cls.env['product.pricelist']
        cls.supplier_info = cls.env['product.supplierinfo']
        cls.uom_unit = cls.env.ref('product.product_uom_unit')

        # Instances: Product attribute
        cls.physical = cls.env.ref('product.product_category_5')

        cls.attribute1 = cls.env.ref('product.product_attribute_1')
        cls.value1 = cls.env.ref('product.product_attribute_value_1')
        cls.value2 = cls.env.ref('product.product_attribute_value_2')

        cls.attribute2 = cls.env.ref('product.product_attribute_2')
        cls.value3 = cls.env.ref('product.product_attribute_value_3')
        cls.value4 = cls.env.ref('product.product_attribute_value_4')

        cls.ipad_template = cls.product_template.create({
            'name': 'Ipad',
            'no_create_variants': 'no',
            'categ_id': cls.physical.id,
            'list_price': 750,
            'standard_price': 500,
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attribute1.id,
                        'value_ids': [(6, 0, [cls.value1.id, cls.value2.id])]
                        }),
                (0, 0, {'attribute_id': cls.attribute2.id,
                        'value_ids': [(6, 0, [cls.value3.id, cls.value4.id])]
                        })
            ],
        })

        cls.ipad_product = cls.ipad_template.product_variant_ids[0]

        cls.iphone_template = cls.product_template.create({
            'name': 'Ipad Retina Display',
            'no_create_variants': 'yes',
            'categ_id': cls.physical.id,
            'list_price': 500,
            'standard_price': 300,
            'uom_id': cls.uom_unit.id,
            'uom_po_id': cls.uom_unit.id,
            'attribute_line_ids': [
                (0, 0, {'attribute_id': cls.attribute1.id,
                        'value_ids': [(6, 0, [cls.value1.id, cls.value2.id])]
                        }),
                (0, 0, {'attribute_id': cls.attribute2.id,
                        'value_ids': [(6, 0, [cls.value3.id, cls.value4.id])]
                        })
            ],
            'seller_ids': [
                (0, False, {
                    'name': cls.env.ref('base.res_partner_1').id,
                    'delay': 3,
                    'min_qty': 1,
                    'price': 300
                }),
                (0, False, {
                    'name': cls.env.ref('base.res_partner_1').id,
                    'delay': 3,
                    'min_qty': 4,
                    'price': 290
                })]
        })

        cls.pricelist = cls.product_pricelist.create({
            'name': 'Pricelist 1',
            'item_ids': [
                (0, False, {
                    'name': 'Rule 20% on ipad product',
                    'product_id': cls.ipad_product.id,
                    'categ_id': cls.physical.id,
                    'min_quantity': 1,
                    'base': 'list_price',
                    'applied_on': '0_product_variant',
                    'compute_price': 'formula',
                    'price_discount': 20,
                }),
                (0, False, {
                    'name': 'Rule 10% on ipad template ',
                    'product_tmpl_id': cls.ipad_template.id,
                    'applied_on': '1_product',
                    'min_quantity': 1,
                    'base': 'list_price',
                    'compute_price': 'formula',
                    'price_discount': 10
                }),
                (0, False, {
                    'name': 'Rule Min qty 4 10% discount iphone template',
                    'product_tmpl_id': cls.iphone_template.id,
                    'applied_on': '1_product',
                    'base': 'list_price',
                    'min_quantity': 4,
                    'compute_price': 'percentage',
                    'percent_price': 10
                })
            ]
        })

    def test_01_price_rule_get_multi(self):
        # Price for ipad product
        # Must be 600
        price = self.pricelist.with_context(
            uom=self.ipad_product.uom_po_id.id, date='2016-01-01'
        ).price_get(self.ipad_product.id, 1)[self.pricelist.id]
        self.assertEqual(price, 750 * 0.8)

    def test_02_price_rule_get_multi_template(self):
        # Price for iphone template with correct partner
        # Price must be 450
        price = self.pricelist.with_context(
            uom=self.iphone_template.uom_po_id.id, date='2016-01-01'
        ).template_price_get(
            self.iphone_template.id, 4, self.env.ref('base.res_partner_1').id
        )[self.pricelist.id]
        self.assertEqual(price, 500 * 0.9)

    def test_03_price_rule_get_multi_template(self):
        # Price for ipad template
        # must be 500
        price = self.pricelist.with_context(
            uom=self.iphone_template.uom_po_id.id, date='2016-01-01'
        ).template_price_get(self.iphone_template.id, 1)[self.pricelist.id]
        self.assertEqual(price, 500)
