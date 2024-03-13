# Copyright 2024 Camptocamp SA (https://www.camptocamp.com).
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def get_paperformat(self):
        # OVERRIDE to allow to define paperformat via context
        if paperformat_id := self.env.context.get("paperformat_id"):
            return self.env["report.paperformat"].browse(paperformat_id)
        return super().get_paperformat()

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        # OVERRIDE to allow to define paperformat via context
        if specific_paperformat_args is None:
            specific_paperformat_args = {}
        if paperformat_xml_id := specific_paperformat_args.get(
            "data-report-paperformat"
        ):
            paperformat_id = self.env.ref(paperformat_xml_id).id
            self = self.with_context(paperformat_id=paperformat_id)
        return super(IrActionsReport, self)._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
