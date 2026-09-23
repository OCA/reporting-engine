# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.exceptions import ValidationError
from odoo.fields import Command
from odoo.tests import common
from odoo.tools import file_open, format_date, format_datetime
from odoo.tools.pdf import PdfFileReader


class TestReportPDFForm(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        filename = "form_example.pdf"
        pdf_content = None
        with file_open(f"report_pdf_form/tests/data/{filename}", "rb") as pdf_file:
            pdf_content = pdf_file.read()
        cls.pdf_attachment = cls.env["ir.attachment"].create(
            {
                "name": filename,
                "raw": pdf_content,
            }
        )
        cls.empty_view = cls.env["ir.ui.view"].create(
            {
                "name": "pdf_form.example",
                "type": "qweb",
                "model_id": cls.env.ref("base.model_res_partner").id,
                "arch_base": "<t />",
            }
        )
        cls.empty_report = cls.env["ir.actions.report"].create(
            {
                "name": "PDF Form example",
                "report_type": "qweb-pdf",
                "model": "res.partner",
                "report_name": "pdf_form.example",
            }
        )
        cls.report_pdf_form = cls.env["report.pdf.form"].create(
            {
                "name": "PDF Form Example",
                "report_id": cls.empty_report.id,
                "pdf_attachment_id": cls.pdf_attachment.id,
                "model_id": cls.env.ref("base.model_res_partner").id,
                "field_mapping_ids": [
                    Command.create(
                        {
                            "pdf_field_name": "form_name",
                            "odoo_field_evaluation": "dotted_path",
                            "odoo_field_value": "name",
                        }
                    ),
                    Command.create(
                        {
                            "pdf_field_name": "form_company",
                            "odoo_field_evaluation": "dotted_path",
                            "odoo_field_value": "company_id.name",
                        }
                    ),
                    Command.create(
                        {
                            "pdf_field_name": "form_user",
                            "odoo_field_evaluation": "code",
                            "odoo_field_value": "env.user.name",
                        }
                    ),
                    Command.create(
                        {
                            "pdf_field_name": "form_line_1",
                            "odoo_field_evaluation": "code",
                            "odoo_field_value": "record.child_ids[0].name if record.child_ids else ''",  # noqa
                        }
                    ),
                    Command.create(
                        {
                            "pdf_field_name": "form_line_2",
                            "odoo_field_evaluation": "code",
                            "odoo_field_value": "record.child_ids[4].name if len(record.child_ids) > 4 else ''",  # noqa
                        }
                    ),
                ],
            }
        )
        cls.azure_partner = cls.env["res.partner"].create(
            {
                "name": "Azure Partner",
                "child_ids": [
                    Command.create({"name": "Child 1"}),
                ],
            }
        )

    @classmethod
    def _get_fields_values_from_reader(cls, reader):
        res = {}
        for pdf_field in reader.trailer["/Root"]["/AcroForm"]["/Annots"]:
            pdf_object = pdf_field.getObject()
            res[pdf_object["/T"].split("__")[1]] = pdf_object["/V"]
        return res

    def test_fill_pdf_form(self):
        streams_dict = self.env["ir.actions.report"]._render_qweb_pdf_prepare_streams(
            "pdf_form.example", {}, res_ids=self.azure_partner.ids
        )
        reader = PdfFileReader(streams_dict[self.azure_partner.id]["stream"])
        fields_values = self._get_fields_values_from_reader(reader)
        for pdf_field_name, pdf_field_value in fields_values.items():
            if pdf_field_name == "form_name":
                self.assertEqual(pdf_field_value, self.azure_partner.name)
            elif pdf_field_name == "form_user":
                self.assertEqual(pdf_field_value, self.env.user.name)
            elif pdf_field_name == "form_company":
                self.assertEqual(pdf_field_value, "")
            elif pdf_field_name == "form_line_1":
                self.assertEqual(pdf_field_value, self.azure_partner.child_ids[0].name)
            elif pdf_field_name == "form_line_2":
                self.assertEqual(pdf_field_value, "")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _new_field(self, path, evaluation="dotted_path"):
        """Build a (non-stored) field mapping to exercise the helpers without
        triggering the dotted-path constraint on persisted records."""
        return self.env["report.pdf.form.field"].new(
            {
                "report_form_id": self.report_pdf_form.id,
                "pdf_field_name": "x",
                "odoo_field_evaluation": evaluation,
                "odoo_field_value": path,
            }
        )

    def _path_value(self, path, record):
        field = self._new_field(path)
        return self.env["ir.actions.report"]._get_pdf_value_from_path(field, record)

    # ------------------------------------------------------------------
    # _get_pdf_value_from_path: value formatting per field type
    # ------------------------------------------------------------------
    def test_format_boolean(self):
        company = self.env["res.partner"].create({"name": "ACME", "is_company": True})
        self.assertEqual(self._path_value("is_company", company), "Yes")
        self.assertEqual(self._path_value("is_company", self.azure_partner), "No")

    def test_format_many2one(self):
        belgium = self.env.ref("base.be")
        self.azure_partner.country_id = belgium
        self.assertEqual(
            self._path_value("country_id", self.azure_partner), belgium.display_name
        )

    def test_format_selection(self):
        selection = dict(
            self.env["res.partner"]._fields["type"]._description_selection(self.env)
        )
        self.assertEqual(
            self._path_value("type", self.azure_partner),
            selection[self.azure_partner.type],
        )

    def test_format_many2many(self):
        tag = self.env["res.partner.category"].create({"name": "VIP"})
        self.azure_partner.category_id = tag
        self.assertEqual(
            self._path_value("category_id", self.azure_partner), tag.display_name
        )

    def test_format_one2many(self):
        expected = ", ".join(c.display_name for c in self.azure_partner.child_ids)
        self.assertEqual(self._path_value("child_ids", self.azure_partner), expected)

    def test_format_datetime(self):
        tz = self.env.user.tz or "UTC"
        expected = format_datetime(
            self.env, self.azure_partner.create_date, tz=tz, dt_format=False
        )
        self.assertEqual(self._path_value("create_date", self.azure_partner), expected)

    def test_format_date(self):
        rate = self.env["res.currency.rate"].create(
            {
                "currency_id": self.env.ref("base.USD").id,
                "name": "2099-01-01",
                "rate": 1.0,
            }
        )
        self.assertEqual(
            self._path_value("name", rate), format_date(self.env, rate.name)
        )

    def test_format_empty_and_other(self):
        # Falsy value -> empty string
        self.assertEqual(self._path_value("ref", self.azure_partner), "")
        # Non specially-handled type falls back to str()
        self.azure_partner.color = 5
        self.assertEqual(self._path_value("color", self.azure_partner), "5")

    def test_path_invalid_returns_empty(self):
        # A path whose first segment does not exist raises AttributeError in
        # mapped() and must be handled gracefully (empty value).
        self.assertEqual(
            self._path_value("does_not_exist.name", self.azure_partner), ""
        )

    # ------------------------------------------------------------------
    # Python code evaluation with reusable variables
    # ------------------------------------------------------------------
    def test_code_eval_with_variable(self):
        self.env["report.pdf.form.variable"].create(
            {
                "report_form_id": self.report_pdf_form.id,
                "name": "greeting",
                "code": "'Hello'",
            }
        )
        code_field = self.env["report.pdf.form.field"].create(
            {
                "report_form_id": self.report_pdf_form.id,
                "pdf_field_name": "greeting_field",
                "odoo_field_evaluation": "code",
                "odoo_field_value": "greeting + ' ' + record.name",
            }
        )
        value = self.env["ir.actions.report"]._get_pdf_value_from_code(
            code_field, self.azure_partner
        )
        self.assertEqual(value, "Hello Azure Partner")

    # ------------------------------------------------------------------
    # Dotted-path validation
    # ------------------------------------------------------------------
    def test_validate_dotted_path(self):
        self.assertTrue(self._new_field("name")._validate_dotted_path())
        self.assertTrue(self._new_field("country_id.name")._validate_dotted_path())
        # Unknown field
        self.assertFalse(self._new_field("does_not_exist")._validate_dotted_path())
        # Traversing through a non-relational field
        self.assertFalse(self._new_field("name.whatever")._validate_dotted_path())
        # Code/text evaluation is always considered valid
        self.assertTrue(self._new_field("anything", "code")._validate_dotted_path())

    def test_compute_validation_message(self):
        name_field = self.report_pdf_form.field_mapping_ids.filtered(
            lambda f: f.pdf_field_name == "form_name"
        )
        self.assertTrue(name_field.is_valid)
        self.assertEqual(name_field.validation_message, "Valid path")
        code_field = self.report_pdf_form.field_mapping_ids.filtered(
            lambda f: f.pdf_field_name == "form_user"
        )
        self.assertEqual(code_field.validation_message, "Validation not applicable")
        invalid = self._new_field("does_not_exist")
        self.assertFalse(invalid.is_valid)
        self.assertIn("Invalid path", invalid.validation_message)

    def test_action_validate_field(self):
        valid = self.report_pdf_form.field_mapping_ids.filtered(
            lambda f: f.pdf_field_name == "form_name"
        )
        self.assertEqual(valid.action_validate_field()["params"]["type"], "success")
        invalid = self._new_field("does_not_exist")
        self.assertEqual(invalid.action_validate_field()["params"]["type"], "danger")

    def test_check_dotted_path_constraint(self):
        with self.assertRaises(ValidationError):
            self.env["report.pdf.form.field"].create(
                {
                    "report_form_id": self.report_pdf_form.id,
                    "pdf_field_name": "bad",
                    "odoo_field_evaluation": "dotted_path",
                    "odoo_field_value": "does_not_exist",
                }
            )

    # ------------------------------------------------------------------
    # report.pdf.form: unique report_id, onchange, preview
    # ------------------------------------------------------------------
    def _create_form(self, report_name, report=None):
        report = report or self.env["ir.actions.report"].create(
            {
                "name": report_name,
                "report_type": "qweb-pdf",
                "model": "res.partner",
                "report_name": report_name,
            }
        )
        return self.env["report.pdf.form"].create(
            {
                "name": report_name,
                "report_id": report.id,
                "pdf_attachment_id": self.pdf_attachment.id,
                "model_id": self.env.ref("base.model_res_partner").id,
                "field_mapping_ids": [
                    Command.create(
                        {
                            "pdf_field_name": "form_name",
                            "odoo_field_evaluation": "dotted_path",
                            "odoo_field_value": "name",
                        }
                    ),
                ],
            }
        )

    def test_unique_report_id_on_create(self):
        with self.assertRaises(ValidationError):
            self.env["report.pdf.form"].create(
                {
                    "name": "Duplicate",
                    "report_id": self.empty_report.id,
                    "pdf_attachment_id": self.pdf_attachment.id,
                    "model_id": self.env.ref("base.model_res_partner").id,
                }
            )

    def test_unique_report_id_on_write(self):
        form2 = self._create_form("pdf_form.example2")
        with self.assertRaises(ValidationError), self.env.cr.savepoint():
            form2.write({"report_id": self.empty_report.id})

    def test_onchange_report_id(self):
        form = self.env["report.pdf.form"].new({"report_id": self.empty_report.id})
        form._onchange_report_id()
        self.assertEqual(form.model_id, self.env.ref("base.model_res_partner"))

    def test_action_preview_pdf(self):
        # Ensure at least one record of the model exists for the sample
        self.assertTrue(self.env["res.partner"].search([], limit=1))
        action = self.report_pdf_form.action_preview_pdf()
        self.assertEqual(action["type"], "ir.actions.act_url")
