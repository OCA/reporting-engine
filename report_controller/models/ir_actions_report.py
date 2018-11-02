# Copyright 2018 Hugo Rodrigues
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import requests
from odoo import models, api, fields, _, exceptions

CONTROLLER_TYPES = [("controller", "Controller")]
CONTROLLER_KEYS = [x[0] for x in CONTROLLER_TYPES]

PDF_MAGIC = b"%PDF"

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"
    _sql_constraints = [
        ("check_controller_url", "CHECK(report_type NOT ILIKE 'controller%' OR controller_url IS NOT NULL)", _("A controller report must have a URL"))
    ]

    report_type = fields.Selection(selection_add=CONTROLLER_TYPES)

    controller_url = fields.Char()

    @api.multi
    def render_controller(self, res_ids, data=None):
        """
        This method gets the PDF report from a URL
        """
        self.ensure_one()
        if not data:
            data = {}

        url = self.controller_url
        if isinstance(res_ids, list) and \
                all([isinstance(x, (int, str)) for x in res_ids]):
            docids = ",".join([str(x) for x in res_ids])
            if url[-1] != "/":
                url += "/"
            url += docids
        response = requests.get(url)
        if response.content[:4] != PDF_MAGIC:
            raise exceptions.ValidationError(_("Controller result isn't a PDF"))
        return response.content, "pdf"
