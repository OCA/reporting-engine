# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, models


class ProductAttributeValue(models.Model):
    _inherit = 'product.attribute.value'

    @api.model
    def create(self, vals):
        """Link created attribute value to the associated template if proceed.

        This happens when quick-creating values from the product configurator.
        """
        attr_value = super(ProductAttributeValue, self).create(vals)
        if 'template_for_attribute_value' in self.env.context:
            template = self.env['product.template'].browse(
                self.env.context['template_for_attribute_value'])
            line = template.attribute_line_ids.filtered(
                lambda x: x.attribute_id == attr_value.attribute_id)
            line.value_ids = [(4, attr_value.id)]
        return attr_value
