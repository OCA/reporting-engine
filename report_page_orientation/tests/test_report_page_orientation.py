# Copyright 2022 Sunflower IT <https://www.sunflowerweb.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import BytesIO

from PyPDF2 import PdfFileReader

from odoo.tests.common import HttpCase


class TestReportPageOrientation(HttpCase):
    def setUp(self):
        super(TestReportPageOrientation, self).setUp()
        report_name = "report_page_orientation.report_page_orientation_demo_report_view"
        self.report_obj = self.env["ir.actions.report"]
        self.report = self.report_obj._get_report_from_name(report_name)
        self.admin_user = self.env.ref("base.user_admin")

    def test_report_generation_pdf(self):
        """Test flow for Report Page Orientation"""

        # This will call _run_wkhtmltopdf -> _build_wkhtmltopdf_args
        # NB: you need to `force_report_rendering=True` or it will default
        # to html instead

        pdf, content_type = (
            self.report.with_user(self.admin_user.id)
            .with_context(force_report_rendering=True)
            ._render_qweb_pdf(self.admin_user.ids)
        )
        # Confirm that pdf content was created
        self.assertTrue(pdf)

        # Convert to pdf and save in variable
        out_pdf = BytesIO(pdf)
        pdf_file = PdfFileReader(out_pdf)

        # No of pages should be at least greater than 1
        self.assertTrue(pdf_file.getNumPages() > 1)

        # Check the first page, it should be Portrait
        self.assertEqual(self.check_pdf_orientation(0, pdf_file), "Portrait")

        # Check random page except the first should be Landscape
        self.assertEqual(self.check_pdf_orientation(2, pdf_file), "Landscape")

    def check_pdf_orientation(self, page_no, pdf_reader):
        # We get/check the rotate attribute of the page
        deg = pdf_reader.getPage(page_no).get("/Rotate")
        page = pdf_reader.getPage(page_no).mediaBox
        if (
            page.getUpperRight_x() - page.getUpperLeft_x()
            > page.getUpperRight_y() - page.getLowerRight_y()
        ):
            if deg in [0, 180, None]:
                return "Landscape"
            else:
                return "Portrait"
        else:
            if deg in [0, 180, None]:
                return "Portrait"
            else:
                return "Landscape"
