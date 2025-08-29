# Copyright 2013 XCG Consulting (http://odoo.consulting)
# Copyright 2025 Akretion France (https://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class Py3oServer(models.Model):
    _name = "py3o.server"
    _description = "LibreOffice UNO Remote Protocol (URP) for Py3o"

    host = fields.Char(
        string="LibreOffice Hostname or IP address",
        default="localhost",
        required=True,
    )
    port = fields.Integer(
        required=True,
        default=8997,
        help="TCP port on which LibreOffice listens. This port is written in the "
        "--accept parameter of the soffice.bin command line.",
    )
    is_active = fields.Boolean("Active", default=True)
    pdf_options_id = fields.Many2one(
        "py3o.pdf.options",
        string="PDF Options",
        ondelete="restrict",
        help="PDF options can be set per Py3o Server but also per report. "
        "If both are defined, the options on the report are used.",
    )

    @api.constrains("port")
    def _check_port(self):
        for rec in self:
            if rec.port < 1 or rec.port > 65535:
                raise ValidationError(
                    _(
                        "The port cannot be set to %(port)s. The value of a TCP port must be "
                        "between 1 and 65535.",
                        rec.port,
                    )
                )

    @api.depends("host", "port")
    def _compute_display_name(self):
        for rec in self:
            dname = rec.host
            if dname and rec.port:
                dname = f"{dname}:{rec.port}"
            rec.display_name = dname
