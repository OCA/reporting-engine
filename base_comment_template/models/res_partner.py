# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    property_comment_template_id = fields.Many2one(
        comodel_name='base.comment.template',
        string='Conditions template',
        company_dependant=True,
    )

    @api.model
    def _commercial_fields(self):
        res = super(ResPartner, self)._commercial_fields()
        res += ['property_comment_template_id']
        return res
