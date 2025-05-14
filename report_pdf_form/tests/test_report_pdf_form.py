# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)

from odoo.fields import Command
from odoo.tests import common
from odoo.tools import file_open
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
        cls.azure_partner = cls.env.ref("base.res_partner_12")

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
