# Copyright 2015 Tecnativa - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ReportCertificate(models.Model):
    _name = "report.certificate"
    _description = "Report Certificate"
    _order = "sequence,id"

    @api.model
    def _default_company(self):
        m_company = self.env["res.company"]
        return m_company._company_default_get("report.certificate")

    sequence = fields.Integer(default=10)
    name = fields.Char(required=True)
    path = fields.Char(
        string="Certificate file path",
        required=True,
        help="Path to PKCS#12 certificate file",
    )
    password_file = fields.Char(
        string="Password file path",
        required=True,
        help="Path to certificate password file",
    )
    model_id = fields.Many2one(
        string="Model",
        required=True,
        comodel_name="ir.model",
        help="Model where apply this certificate",
        ondelete="cascade",
    )
    domain = fields.Char(
        string="Domain",
        help="Domain for filtering if sign or not the document",
    )
    action_report_ids = fields.Many2many(
        string="Allowed reports",
        help="Reports to sign for the selected model."
        "No report selected means all reports are allowed.",
        comodel_name="ir.actions.report",
        relation="report_certificate_action_report",
        column1="report_certificate_id",
        column2="action_report_id",
        domain="[('model_id', '=', model_id)]",
    )
    allow_only_one = fields.Boolean(
        string="Allow only one document",
        default=True,
        help="If True, this certificate can not be useb to sign "
        "a PDF from several documents.",
    )
    attachment = fields.Char(
        string="Save as attachment",
        help="Filename used to store signed document as attachment. "
        "Keep empty to not save signed document.",
    )
    company_id = fields.Many2one(
        string="Company",
        comodel_name="res.company",
        required=True,
        default=_default_company,
    )
    signing_method = fields.Selection(
        selection=[("java", "Java"), ("endesive", "Endesive")],
        default="java",
        string="Signing Method",
        required=True,
    )
    endesive_certificate_mail = fields.Char(
        string="Signature e-mail",
        help="E-mail address to include in PDF digital signature.",
    )
    endesive_certificate_location = fields.Char(
        string="Signature location",
        help="Location to include in digital signature (typically, a city name). ",
    )
    endesive_certificate_reason = fields.Char(
        string="Signature reason",
        help="Reason text to include in digital signature.",
    )
