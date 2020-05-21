# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from suds.client import Client


class JasperServerConfig(models.Model):
    _name = "jasper.server.config"
    _description = "Jasper Server Config"

    name = fields.Char(
        string="Description",
        required=True,
    )
    jasper_url = fields.Char(
        string="Jasper Server URL",
        default="http://localhost:8080/jasperserver/services/repository?wsdl",
    )
    jasper_username = fields.Char(
        string="User Name",
    )
    jasper_password = fields.Char(
        string="Password",
    )
    active = fields.Boolean(
        string="Active",
        default=True,
    )
    report_ids = fields.One2many(
        comodel_name="ir.actions.report",
        inverse_name="jasper_server_config_id",
        string="Report",
    )

    @api.constrains("active")
    def _check_active(self):
        for rec in self:
            if not rec.active and rec.report_ids:
                raise UserError(_("Can not inactive because there are some report reference this record."))

    def connect_jasperserver(self):
        return Client(
            self.jasper_url,
            username=self.jasper_username,
            password=self.jasper_password,
            retxml=True,
        )

    def test_connect_jasperserver(self):
        error = False
        try:
            self.connect_jasperserver()
        except Exception as ex:
            error = ex
        if not error:
            raise UserError(_("Connection success."))
        else:
            raise UserError(_(error))