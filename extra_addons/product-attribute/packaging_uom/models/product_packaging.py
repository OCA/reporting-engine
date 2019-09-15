# Copyright 2015-2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    @api.model
    def _default_uom_categ_domain_id(self):
        """
        Taking value from context depending from which form it was called
        :return:
        """
        product_id = self.env.context.get("default_product_id")
        categ_id = self.env.context.get('get_uom_categ_from_uom')
        if not product_id and not categ_id:
            return self.env['uom.category']
        if categ_id:
            uom = self.env['uom.uom'].browse(categ_id)
        if product_id:
            uom = self.env['product.product'].browse(product_id).uom_id
        return uom.category_id.id

    uom_id = fields.Many2one(
        'uom.uom',
        'Packaging Unit of Measure',
        help="It must be in the same category than "
             "the default unit of measure.",
        required=False
    )
    uom_categ_domain_id = fields.Many2one(
        default=lambda self: self._default_uom_categ_domain_id(),
        comodel_name='uom.category'
    )
    qty = fields.Float(
        compute="_compute_qty",
        inverse="_inverse_qty",
        store=True,
        readonly=True
    )

    @api.multi
    @api.depends('uom_id', 'product_id.uom_id')
    def _compute_qty(self):
        """
        Compute the quantity by package based on uom
        """
        for packaging in self:
            if packaging.uom_id and packaging.product_id:
                packaging.qty = packaging.uom_id._compute_quantity(
                    1, to_unit=packaging.product_id.uom_id)
            else:
                packaging.qty = 0

    @api.onchange('product_id')
    def onchange_product_id(self):
        self.uom_categ_domain_id = self.product_id.uom_id.category_id.id

    @api.multi
    def _inverse_qty(self):
        """
        The inverse method is defined to make the code compatible with
        existing modules and to not break tests...
        :return:
        """
        for packaging in self:
            category_id = packaging.product_id.uom_id.category_id
            uom_id = packaging.uom_id.search([
                ("factor", "=", 1.0 / self.qty),
                ('category_id', '=', category_id.id)])
            if not uom_id:
                uom_id = packaging.uom_id.create({
                    'name': "%s %s" % (category_id.name, packaging.qty),
                    'category_id': category_id.id,
                    'rounding': packaging.product_id.uom_id.rounding,
                    'uom_type': 'bigger',
                    'factor_inv': packaging.qty,
                    'active': True
                })
            packaging.uom_id = uom_id

    @api.multi
    @api.constrains('uom_id')
    def _check_uom_id(self):
        """ Check uom_id is not null

        Since the field can be computed by the inverse method on 'qty',
        it's no more possible to add a sql constrains on the column uom_id.
        """
        for rec in self:
            if not rec.uom_id:
                raise ValidationError(_("The field Unit of Measure is "
                                        "required"))
