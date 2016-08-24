# -*- coding: utf-8 -*-
# © 2013-2014 Nicolas Bessi (Camptocamp SA)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from openerp import models, fields, api


class BaseCommentTemplate(models.Model):
    _name = "base.comment.template"
    _description = "Base comment template"

    name = fields.Char('Comment summary', required=True)
    position = fields.Selection([('before_lines', 'Before lines'),
                                 ('after_lines', 'After lines')],
                                'Position',
                                required=True,
                                default='before_lines',
                                help="Position on document")
    text = fields.Html('Comment', translate=True, required=True)

    @api.multi
    def get_value(self, partner_id=False):
        self.ensure_one()
        lang = None
        if partner_id:
            lang = self.env['res.partner'].browse(partner_id).lang
        return self.with_context({'lang': lang}).text
