# Copyright 2025 Dixmit
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import api, fields, models


class ReportInstance(models.Model):
    _name = "report.instance"
    _description = "Instance of Report"

    name = fields.Char(required=True)
    template_id = fields.Many2one("report.template", required=True)
    source = fields.Selection(related="template_id.source", store=True)
    show_search_bar = fields.Boolean(default=False)
    search_view_id = fields.Many2one(related="template_id.search_view_id")
    search_res_model = fields.Char(related="template_id.search_model_id.model")
    show_settings = fields.Boolean(default=True)
    show_pivot_date = fields.Boolean(default=True)
    base_date = fields.Date()
    currency_id = fields.Many2one(
        "res.currency",
        required=True,
        default=lambda self: self.env.company.currency_id,
    )

    data = fields.Json(compute="_compute_data")
    column_ids = fields.One2many(
        "report.instance.column",
        "instance_id",
    )
    active = fields.Boolean(default=True)

    @api.depends("template_id", "column_ids")
    def _compute_data(self):
        for record in self:
            record.data = record._get_data()

    def _get_data(self):
        rows = []
        style = self.template_id.style_id._get_style()
        for kpi in self.template_id.kpi_ids:
            kpi_style, kpi_parameters = kpi.style_id._get_style_css(style)
            rows.append(
                {
                    "id": kpi.id,
                    "name": kpi.name,
                    "is_currency": kpi.is_currency,
                    "style": kpi_style,
                    "parameters": kpi_parameters,
                    "invisible": kpi.invisible,
                }
            )
        columns = self.column_ids._get_data()
        return {
            "date": fields.Date.to_string(self.base_date or fields.Date.today()),
            "rows": rows,
            "columns": columns,
        }

    def process_information(self, pivot_date, domain=None):
        self.ensure_one()
        cols = self.column_ids._get_data(fields.Date.from_string(pivot_date))
        kpi_data = {}
        self.template_id.kpi_ids._process_information(
            cols, kpi_data, domain=domain, **self._extra_process_keys()
        )
        return kpi_data

    def _extra_process_keys(self):
        """
        This method can be overridden in subclasses to provide extra keys
        for the _process_information method.
        """
        return {}

    def view_report_instance(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "report_builder.report_instance_view_act_window"
        )
        action.update({"res_id": self.id})
        return action

    def get_display_settings_action(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"]._for_xml_id(
            "report_builder.report_instance_act_window"
        )
        action.update(
            {
                "res_id": self.id,
                "view_mode": "form",
                "views": [view for view in action["views"] if view[1] == "form"],
            }
        )
        return action

    def get_pdf_report_action(self, pivot_date, domain=None):
        # TODO: implement the method to return the action for PDF report generation
        self.ensure_one()
        return self.env.ref("report_builder.qweb_pdf_export").report_action(
            self, data={"pivot_date": pivot_date, "domain": domain}
        )

    def get_xlsx_report_action(self, pivot_date, domain=None):
        self.ensure_one()
        return self.env.ref("report_builder.xlsx_export").report_action(
            self, data={"pivot_date": pivot_date, "domain": domain}
        )
