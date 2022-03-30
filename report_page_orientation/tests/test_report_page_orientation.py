# Copyright 2022 Sunflower IT <https://www.sunflowerweb.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import BytesIO
from re import findall

from odoo.tests.common import HttpCase
from PyPDF2 import PdfFileReader


class TestReportPageOrientation(HttpCase):
    def setUp(self):
        super(TestReportPageOrientation, self).setUp()
        self.report = self.env.ref(
            "report_page_orientation.report_page_orientation_demo_reports"
        )

    def test_report_generation_pdf(self):
        """ Test flow for Report Page Orientation """

        existing_users = self.env["res.users"].search([])

        # Html content test
        html_content = self.report._render_qweb_html(existing_users.ids)[0]
        self.assertTrue(html_content)

        decoded_pdf = html_content.decode("utf-8")

        # Let try to see if the qweb was created with usernames
        users = [
            findall(r"\b%s\b" % user_name, decoded_pdf)[0]
            for user_name in existing_users.mapped("name")
        ]
        self.assertListEqual(users, existing_users.mapped("name"))

        # This will call _run_wkhtmltopdf -> _build_wkhtmltopdf_args
        # NB: you need to `force_report_rendering=True` or it will default
        # to html instead

        pdf, content_type = self.report.with_context(
            force_report_rendering=True
        )._render_qweb_pdf(existing_users.ids)
        # Confirm that pdf content was created
        self.assertTrue(pdf)

        # Convert to pdf and save in variable
        out_pdf = BytesIO(pdf)
        pdf_file = PdfFileReader(out_pdf)

        # No of pages should be at least greater than 1
        self.assertTrue((pdf_file.getNumPages() > 1))

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
