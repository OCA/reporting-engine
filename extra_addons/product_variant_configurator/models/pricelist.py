# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# Copyright 2017 David Vidal <david.vidal@tecnativa.com>
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import api, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    @api.multi
    def _compute_price_rule(self, products_qty_partner, date=False,
                            uom_id=False):
        """Overwrite for covering the case where templates are passed and a
        different uom is used."""
        if products_qty_partner[0][0]._name != "product.template":
            # Standard use case - Nothing to do
            return super(ProductPricelist, self)._compute_price_rule(
                products_qty_partner, date=date, uom_id=uom_id,
            )
        # Isolate object
        pricelist_obj = self
        if not uom_id and pricelist_obj.env.context.get('uom'):
            ctx = dict(pricelist_obj.env.context)
            # Remove uom context for avoiding the re-processing
            uom_id = ctx.pop('uom')
            pricelist_obj = pricelist_obj.with_context(ctx)
        if uom_id:
            # rebrowse templates with uom if given
            tmpl_ids = [item[0].id for item in products_qty_partner]
            tmpl_obj = self.env['product.template']
            tmpls = tmpl_obj.with_context(uom=uom_id).browse(tmpl_ids)
            products_qty_partner = [
                (tmpls[index], data_struct[1], data_struct[2])
                for index, data_struct in enumerate(products_qty_partner)
            ]
        return super(ProductPricelist, pricelist_obj)._compute_price_rule(
            products_qty_partner, date=date, uom_id=False,
        )

    @api.multi
    def template_price_get(self, prod_id, qty, partner=None):
        return dict((key, price[0]) for key, price in
                    self.template_price_rule_get(prod_id, qty,
                                                 partner=partner).items())

    @api.multi
    def template_price_rule_get(self, prod_id, qty, partner=None):
        product = self.env['product.template'].browse([prod_id])
        return self.price_rule_get_multi(
            products_by_qty_by_partner=[(product, qty, partner)])[prod_id]
