# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from odoo import api, fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("qweb-xml", "XML")], ondelete={"qweb-xml": "set default"}
    )
    xsd_schema = fields.Binary(
        string="XSD Validation Schema",
        attachment=True,
        help="File with XSD Schema for checking content of result report. Can be empty "
        "if validation is not required.",
    )
    xml_encoding = fields.Selection(
        selection=[
            ("UTF-8", "UTF-8")  # will be used as default even if nothing is selected
        ],
        string="XML Encoding",
        help="Encoding for XML reports. If nothing is selected, then UTF-8 will be "
        "applied.",
    )
    xml_declaration = fields.Boolean(
        string="XML Declaration",
        help='Add `<?xml encoding="..." version="..."?>` at the start of final report '
        "file.",
    )
    xml_extension = fields.Char(
        default="xml",
        help="Extension for XML Reports, by default is `xml`",
    )

    @api.model
    def _render_qweb_xml(self, report_ref, res_ids, data=None):
        """
        Call `generate_report` method of report abstract class
        `report.<report technical name>` or of standard class for XML report
        rendering - `report.report_xml.abstract`

        Args:
         * docids(list) - IDs of instances for those report will be generated
         * data(dict, None) - variables for report rendering

        Returns:
         * str - result content of report
         * str - type of result content
        """
        report = self._get_report(report_ref)
        report_model = self.env.get(
            f"report.{report.report_name}", self.env["report.report_xml.abstract"]
        )
        return report_model.generate_report(
            ir_report=report,  # will be used to get settings of report
            docids=res_ids,
            data=data or {},
        )
