# Copyright 2017 Avoin.Systems
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import odoo.tests
from odoo.exceptions import ValidationError
from odoo.tests.common import tagged


@tagged("post_install", "-at_install")
class TestWkhtmltopdf(odoo.tests.TransactionCase):
    def _get_custom_params(self, names, values=None):
        if type(names) == list:
            pass
        else:
            names = [names]
        if type(values) == list:
            pass
        else:
            values = [values]
        params = []
        for i, name in enumerate(names):
            try:
                value = values[i]
            except IndexError:
                value = None
            param = {"name": name}
            if value is not None:
                param["value"] = value
            params.append((0, 0, param))
        return {"custom_params": params}

    def test_wkhtmltopdf_incorrect_parameter(self):
        name = "bad-parameter"
        for report_paperformat in self.env["report.paperformat"].search([]):
            with self.assertRaises(ValidationError):
                report_paperformat.update(self._get_custom_params(name))

    def test_wkhtmltopdf_valid_parameter(self):
        IrActionsReport = self.env["ir.actions.report"]
        names = ["--dpi", "--disable-smart-shrinking", "--quiet"]
        values = "360"
        error_message = "There was an error adding wkhtmltopdf parameter "
        for report_paperformat in self.env["report.paperformat"].search([]):
            command_args = IrActionsReport._build_wkhtmltopdf_args(
                report_paperformat, None
            )
            count = len(command_args)
            error = False
            try:
                report_paperformat.update(self._get_custom_params(names, values))
            except ValidationError:
                error = True
            self.assertEqual(
                error,
                False,
                error_message + ", ".join(names),
            )
            command_args = IrActionsReport._build_wkhtmltopdf_args(
                report_paperformat, None
            )
            self.assertEqual(count + 1, len(command_args))

    def test_wkhtmltopdf_duplicated_parameter(self):
        IrActionsReport = self.env["ir.actions.report"]
        for report_paperformat in self.env["report.paperformat"].search([]):
            command_args = IrActionsReport._build_wkhtmltopdf_args(
                report_paperformat,
                None,
            )
            self.assertEqual(command_args.count("--zoom"), 1)
            value_index = command_args.index("--zoom") + 1
            self.assertNotEqual(command_args[value_index], "1.0")

            error = False
            try:
                report_paperformat.update(self._get_custom_params("--zoom", "1.0"))
            except ValidationError:
                error = True
            self.assertEqual(error, False)
            command_args = IrActionsReport._build_wkhtmltopdf_args(
                report_paperformat,
                None,
            )
            self.assertEqual(command_args.count("--zoom"), 1)
            self.assertEqual(command_args[value_index], "1.0")
