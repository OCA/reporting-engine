# Copyright 2017 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ProductTemplateTag(models.Model):

    _name = 'product.template.tag'
    _description = 'Product Tag'

    name = fields.Char(string="Name", required=True, translate=True)
    color = fields.Integer(string="Color Index")
    product_tmpl_ids = fields.Many2many(
        comodel_name='product.template', string="Products",
        relation='product_template_product_tag_rel',
        column1='tag_id', column2='product_tmpl_id')
    products_count = fields.Integer(
        string="# of Products", compute='_compute_products_count', store=True)
    company_id = fields.Many2one(
        comodel_name='res.company', string="Company",
        default=lambda self: self._default_company())

    @api.model
    def _default_company(self):
        return self.env['res.users']._get_company()

    @api.multi
    @api.depends('product_tmpl_ids')
    def _compute_products_count(self):
        for rec in self:
            rec.products_count = len(rec.product_tmpl_ids)
