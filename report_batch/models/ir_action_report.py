# Copyright (C) 2019 IBM Corp.
# Copyright (C) 2019 Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import random

from odoo import api, fields, models


class IrActionsReportSubreport(models.Model):
    _name = "ir.actions.report.subreport"
    _description = "Report Subreport"
    _order = "sequence"

    parent_report_id = fields.Many2one("ir.actions.report", ondelete="cascade")
    sequence = fields.Integer(default=10)
    model = fields.Char(related="parent_report_id.model")
    subreport_id = fields.Many2one(
        "ir.actions.report", string="Subreport", required=True
    )


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    subreport_ids = fields.One2many("ir.actions.report.subreport", "parent_report_id")

    def generate_top_part(self):
        return (
            """<?xml version="1.0"?>\n\t<t t-name="%s">\n\t
        """
            % self.report_name
        )

    def generate_bottom_part(self):
        return """\n
        \t\t</t>\n\t\t"""

    def generate_custom_content(self, report_name):
        return (
            """\n
        \t<t t-call="%s"/>"""
            % report_name
        )

    def _generate_batch_qweb_report(self, update_batch_qweb=False):
        report_name = self.report_name
        if "." in report_name:
            module = self.report_name.split(".")[0]
            report_name = self.report_name.split(".")[1]
        else:
            # Generate random number to avoid IntegrityError
            module = random.randint(1, 1000000)
            self.report_name = "{}.{}".format(module, report_name)
        if self.subreport_ids:
            if update_batch_qweb:
                report_name = self.report_name.split(".")[1]
                # Delete old Qweb batch report
                model_data = self.env["ir.model.data"].search(
                    [("res_id", "=", self.id)]
                )
                model_data.unlink()
                ui_view = self.env["ir.ui.view"].search([("name", "=", report_name)])
                ui_view.unlink()
            template_header = self.generate_top_part()
            template_footer = self.generate_bottom_part()
            template_content = ""

            for subreport in self.subreport_ids:
                template_content += self.generate_custom_content(
                    subreport.subreport_id.report_name
                )
            data = "{}{}{}".format(template_header, template_content, template_footer)
            ui_view = self.env["ir.ui.view"].create(
                {
                    "name": report_name,
                    "type": "qweb",
                    "model": self.model,
                    "mode": "primary",
                    "arch_base": data,
                }
            )
            self.env["ir.model.data"].create(
                {
                    "module": module,
                    "name": report_name,
                    "res_id": ui_view.id,
                    "model": "ir.ui.view",
                }
            )
            # Register batch report option
            if not self.binding_model_id:
                self.create_action()
        return True

    @api.model
    def create(self, vals):
        res = super(IrActionsReport, self).create(vals)
        for report in res:
            report._generate_batch_qweb_report()
        return res

    def write(self, vals):
        res = super(IrActionsReport, self).write(vals)
        if "subreport_ids" in vals or "model" in vals:
            for report in self:
                report._generate_batch_qweb_report(update_batch_qweb=True)
        return res
