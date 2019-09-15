# Copyright 2015 Oihane Crucelaegui - AvanzOSC
# Copyright 2016 Pedro M. Baeza <pedro.baeza@tecnativa.com>
# Copyright 2016 ACSONE SA/NV
# License AGPL-3 - See http://www.gnu.org/licenses/agpl-3

from odoo import _, api, fields, models
from odoo.tools import config


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    no_create_variants = fields.Selection(
        [('yes', "Don't create them automatically"),
         ('no', "Create them automatically"),
         ('empty', 'Use the category value')],
        string='Variant creation', required=True, default='empty',
        help="This selection defines if variants for all attribute "
             "combinations are going to be created automatically at saving "
             "time.")

    @api.onchange('no_create_variants')
    def onchange_no_create_variants(self):
        if self.no_create_variants in ['no', 'empty'] and \
                self._origin.no_create_variants:
            # the test on self._origin.no_create_variants is to
            # avoid the warning when opening a new form in create
            # mode (ie when the onchange triggers when Odoo sets
            # the default value)
            return {'warning':
                    {'title': _('Change warning!'),
                     'message': _('Changing this parameter may cause'
                                  ' automatic variants creation')}
                    }

    @api.model
    def create(self, vals):
        if 'product_name' in self.env.context:
            # Needed because ORM removes this value from the dictionary
            vals['name'] = self.env.context['product_name']
        return super(ProductTemplate, self).create(vals)

    @api.multi
    def write(self, values):
        res = super(ProductTemplate, self).write(values)
        if 'no_create_variants' in values:
            self.create_variant_ids()
        return res

    @api.multi
    def _get_product_attributes_dict(self):
        return self.attribute_line_ids.mapped(
            lambda x: {'attribute_id': x.attribute_id.id})

    @api.multi
    def create_variant_ids(self):
        obj = self.with_context(creating_variants=True)
        if (config['test_enable'] and
                not self.env.context.get('check_variant_creation')):
            return super(ProductTemplate, obj).create_variant_ids()
        for tmpl in obj:
            if ((tmpl.no_create_variants == 'empty' and
                    not tmpl.categ_id.no_create_variants) or
                    tmpl.no_create_variants == 'no' or
                    not tmpl.attribute_line_ids):
                super(ProductTemplate, tmpl).create_variant_ids()
        return True

    @api.multi
    def action_open_attribute_prices(self):
        self.ensure_one()
        price_obj = self.env['product.attribute.price']
        for line in self.attribute_line_ids:
            for value in line.value_ids:
                prices = price_obj.search([('product_tmpl_id', '=', self.id),
                                           ('value_id', '=', value.id)])
                if not prices:
                    price_obj.create({
                        'product_tmpl_id': self.id,
                        'value_id': value.id,
                    })
        return self.env.ref('product_variant_configurator.'
                            'attribute_price_action').read()[0]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        # Make a search with default criteria
        temp = super(models.Model, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        # Make the other search
        temp += super(ProductTemplate, self).name_search(
            name=name, args=args, operator=operator, limit=limit)
        # Merge both results
        res = []
        keys = []
        for val in temp:
            if val[0] not in keys:
                res.append(val)
                keys.append(val[0])
                if limit and len(res) >= limit:
                    break
        return res
