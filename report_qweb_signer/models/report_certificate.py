# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, fields, models


class ReportCertificate(models.Model):
    _name = 'report.certificate'
    _order = 'sequence,id'

    @api.model
    def _default_company(self):
        m_company = self.env['res.company']
        return m_company._company_default_get('report.certificate')

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    path = fields.Char(
        string="Certificate file path", required=True,
        help="Path to PKCS#12 certificate file")
    password_file = fields.Char(
        string="Password file path", required=True,
        help="Path to certificate password file")
    model_id = fields.Many2one(
        string="Model", required=True,
        comodel_name='ir.model',
        help="Model where apply this certificate")
    domain = fields.Char(
        string="Domain",
        help="Domain for filtering if sign or not the document")
    allow_only_one = fields.Boolean(
        string="Allow only one document", default=True,
        help="If True, this certificate can not be useb to sign "
             "a PDF from several documents.")
    attachment = fields.Char(
        string="Save as attachment",
        help="Filename used to store signed document as attachment. "
             "Keep empty to not save signed document.")
    company_id = fields.Many2one(
        string='Company', comodel_name='res.company',
        required=True, default=_default_company)
