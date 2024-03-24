# Copyright 2024 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import fields, models


class Py3oTemplate(models.Model):
    _inherit = 'py3o.template'

    py3o_has_index = fields.Boolean(
        "Has Py3o Index?",
        default=False,
        help="Check if the template has a py3o index. "
             "It needs to be compiled twice to get the index right."
    )
