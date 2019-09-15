# Copyright 2015-2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import odoo.tests.common as common
from odoo.exceptions import ValidationError


class TestProductPackaging(common.TransactionCase):

    def setUp(self):
        super(TestProductPackaging, self).setUp()
        self.uom_unit = self.env.ref('uom.product_uom_unit')
        self.uom_dozen = self.env.ref('uom.product_uom_dozen')
        self.product_dozen = self.env['product.product'].create({
            'name': 'PRODUCT DOZEN',
            'uom_id': self.uom_dozen.id,
        })
        self.product_unit = self.env['product.product'].create({
            'name': 'PRODUCT UNIT',
            'uom_id': self.uom_unit.id,
        })

    def test_compute_quantity_by_package(self):
        """ Create a packagings with uom product_uom_dozen on
                * product_dozen (uom is product_uom_dozen)
                * product_unit (uom is product_uom_unit)
            Result should be :
                * product_dozen -> qty by package : 1
                * product_unit -> qty by package : 12
            Create product_uom_24
            Update product_dozen to set this new uom
            Result should be :
                * product_dozen -> qty by package : 0.5
            Update product_package_unit to set this new uom
            Result should be :
                * product_packaging_unit -> qty by package : 24
            Create product_uom 6
            Update product_dozen to set this new uom
            Result should be :
                * product_packaging_dozen -> qty by package : 2
            Update product_packaging_unit to set this new uom
            Result should be :
                * product_packaging_unit -> qty by package : 6
        """

        packaging_obj = self.env['product.packaging']
        product_packaging_dozen = packaging_obj.create({
            'name': 'PACKAGING 1',
            'product_id': self.product_dozen.id,
            'uom_id': self.uom_dozen.id,
        })
        self.assertAlmostEqual(product_packaging_dozen.qty, 1)
        product_packaging_unit = packaging_obj.with_context(
            default_product_id=self.product_unit.id).create({
                'name': 'PACKAGING 2',
                'product_id': self.product_unit.id,
                'uom_id': self.uom_dozen.id,
            })
        self.assertAlmostEqual(product_packaging_unit.qty, 12)
        self.assertEqual(
            self.uom_dozen.category_id,
            product_packaging_unit.uom_categ_domain_id,
            'The UOM domain is not well set'
        )
        product_uom_24 = self.env['uom.uom'].create({
            'category_id': self.env.ref('uom.product_uom_categ_unit').id,
            'name': 'Double Dozens',
            'factor_inv': 24,
            'uom_type': 'bigger',
        })
        self.product_dozen.uom_id = product_uom_24
        self.assertAlmostEqual(product_packaging_dozen.qty, 0.5)
        product_packaging_unit.uom_id = product_uom_24
        self.assertAlmostEqual(product_packaging_unit.qty, 24)
        product_uom_6 = self.env['uom.uom'].create({
            'category_id': self.env.ref('uom.product_uom_categ_unit').id,
            'name': 'Demi Dozens',
            'factor_inv': 6,
            'uom_type': 'bigger',
        })
        self.product_dozen.uom_id = product_uom_6
        self.assertAlmostEqual(product_packaging_dozen.qty, 2)
        product_packaging_unit.uom_id = product_uom_6
        self.assertAlmostEqual(product_packaging_unit.qty, 6)
        # Set Packaging Quantity
        product_packaging_dozen.qty = 1
        self.assertEqual(
            self.uom_unit,
            product_packaging_dozen.uom_id
        )
        # Try to set null on uom
        with self.assertRaises(ValidationError):
            product_packaging_dozen.uom_id = None

        # Define a new packaging unit
        uom_524 = self.env['uom.uom'].search([
            ('category_id', '=',
             product_packaging_dozen.product_id.uom_id.category_id.id),
            ('name',
             '=',
             '%s %s' %
             (product_packaging_dozen.product_id.uom_id.category_id.name,
              float(524)))
            ])
        self.assertEqual(0, len(uom_524))
        product_packaging_dozen.qty = 524
        uom_524 = self.env['uom.uom'].search([
            ('category_id', '=',
             product_packaging_dozen.product_id.uom_id.category_id.id),
            ('name',
             '=',
             '%s %s' %
             (product_packaging_dozen.product_id.uom_id.category_id.name,
              float(524)))
            ])
        self.assertEqual(1, len(uom_524))
