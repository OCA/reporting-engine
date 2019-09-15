# Copyright 2017 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    state = fields.Selection(selection=[
        ('draft', 'In Development'),
        ('sellable', 'Normal'),
        ('end', 'End of Lifecycle'),
        ('obsolete', 'Obsolete')],
        string='Status',
        default='sellable',
        index=True
    )
