# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import models, fields


class ResCompany(models.Model):
    _inherit = 'res.company'

    report_certificate_ids = fields.One2many(
        string="PDF report certificates",
        comodel_name='report.certificate',
        inverse_name='company_id')
