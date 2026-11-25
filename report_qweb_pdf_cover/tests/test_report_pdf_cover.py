from base64 import b64encode
from io import BytesIO
from itertools import product
from unittest.mock import patch

from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger
from odoo.tools.pdf import PdfReader, PdfWriter

from ..models.ir_actions_report import Report


class TestReportPdfCover(TransactionCase):
    @staticmethod
    def _pdf(widths):
        writer = PdfWriter()
        for width in widths:
            writer.addBlankPage(width=width, height=300)
        stream = BytesIO()
        writer.write(stream)
        return stream.getvalue()

    def test_cover_combinations(self):
        report = self.env["ir.actions.report"]
        front = PdfReader(BytesIO(self._pdf([100])))
        back = PdfReader(BytesIO(self._pdf([100])))
        for count, use_front, use_back, overlap_front, overlap_back in product(
            (1, 2), (False, True), (False, True), (False, True), (False, True)
        ):
            with self.subTest(
                count=count,
                front=use_front,
                back=use_back,
                overlap_front=overlap_front,
                overlap_back=overlap_back,
            ):
                pages = PdfReader(BytesIO(self._pdf([100, 200][:count]))).pages
                writer = PdfWriter()
                report.insert_cover_pages(
                    writer,
                    pages,
                    front,
                    back,
                    use_front,
                    use_back,
                    overlap_front,
                    overlap_back,
                )
                stream = BytesIO()
                writer.write(stream)
                result = PdfReader(BytesIO(stream.getvalue()))
                expected_widths = [100, 200][:count]
                if use_front and not overlap_front:
                    expected_widths.insert(0, 100)
                if use_back and not overlap_back:
                    expected_widths.append([100, 200][count - 1])
                self.assertEqual(
                    [float(page.mediaBox.getWidth()) for page in result.pages],
                    expected_widths,
                )

    @mute_logger("odoo.addons.report_qweb_pdf_cover.models.ir_actions_report")
    def test_empty_and_multipage_covers(self):
        report = self.env["ir.actions.report"]
        for front in (False, True):
            self.assertFalse(report.pdf_check_pages(0, front=front))
            self.assertTrue(report.pdf_check_pages(1, front=front))
            self.assertTrue(report.pdf_check_pages(2, front=front))

    @mute_logger("odoo.addons.report_qweb_pdf_cover.models.ir_actions_report")
    def test_invalid_covers(self):
        report = self.env["ir.actions.report"]
        front, _front_pdf, back, _back_pdf = report.load_cover_pdfs(
            b"invalid", b"invalid", True, True
        )
        self.assertFalse(front)
        self.assertFalse(back)

    @mute_logger("odoo.addons.report_qweb_pdf_cover.models.ir_actions_report")
    def test_render_with_covers(self):
        report = self.env["ir.actions.report"].create(
            {
                "name": "PDF cover test",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "report_qweb_pdf_cover.test_report",
            }
        )
        original = self._pdf([100, 200])
        cover = b64encode(self._pdf([100]))
        empty_cover = b64encode(self._pdf([]))
        invalid_cover = b64encode(b"invalid")
        # Mock the next implementation after this addon's override.
        mro = type(report).__mro__
        parent = next(
            cls
            for cls in mro[mro.index(Report) + 1 :]
            if "_run_wkhtmltopdf" in cls.__dict__
        )

        cases = [
            ("disabled", False, False, False, False, False, False, 2),
            ("missing", True, True, False, False, False, False, 2),
            ("front", True, False, cover, False, False, False, 3),
            ("back", False, True, False, cover, False, False, 3),
            ("both", True, True, cover, cover, False, False, 4),
            ("overlap", True, True, cover, cover, True, True, 2),
            ("empty", True, True, empty_cover, empty_cover, False, False, 2),
            ("invalid", True, True, invalid_cover, invalid_cover, False, False, 2),
        ]

        with patch.object(parent, "_run_wkhtmltopdf", return_value=original):
            for (
                name,
                use_front,
                use_back,
                front_pdf,
                back_pdf,
                overlap_front,
                overlap_back,
                expected_pages,
            ) in cases:
                report.write(
                    {
                        "use_front_cover": use_front,
                        "use_back_cover": use_back,
                        "front_cover_pdf": front_pdf,
                        "back_cover_pdf": back_pdf,
                        "front_cover_overlap": overlap_front,
                        "back_cover_overlap": overlap_back,
                    }
                )
                # Exercise both report-record settings and lookup fallback.
                for renderer in (report, self.env["ir.actions.report"]):
                    with self.subTest(name=name, on_record=bool(renderer)):
                        result = renderer._run_wkhtmltopdf(
                            ["<html/>"], report_ref=report.report_name
                        )
                        self.assertEqual(
                            len(PdfReader(BytesIO(result)).pages), expected_pages
                        )
                        if name in ("disabled", "missing"):
                            self.assertEqual(result, original)
