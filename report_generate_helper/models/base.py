# Copyright 2023 Akretion (https://www.akretion.com).
# @author Matthieu SAISON <matthieu.saison@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models
from odoo.tools.safe_eval import safe_eval, time


class Base(models.AbstractModel):
    _inherit = "base"

    def _generate_report(self, report_name):
        """
        Generate the report matching the report_name for the self object

        The method will return a tuple with the name of the field and the content
        return (filename, content)
        """
        report = self.env["ir.actions.report"]._get_report(report_name)

        method_name = report._get_report_converter()
        method = getattr(self.env["ir.actions.report"], method_name)
        content, extension = method(report_name, self.ids)

        if report.print_report_name and len(self) == 1:
            report_name = safe_eval(
                report.print_report_name, {"object": self, "time": time}
            )
        else:
            report_name = report.name
        filename = "%s.%s" % (report_name, extension)

        return filename, content
