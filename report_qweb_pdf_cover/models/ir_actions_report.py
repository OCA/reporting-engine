# Copyright 2024 ForgeFlow S.L. (https://www.forgeflow.com)
# Part of ForgeFlow. See LICENSE file for full copyright and licensing details.

from base64 import b64decode
from io import BytesIO
from logging import getLogger

from PyPDF2 import PdfFileReader, PdfFileWriter

from odoo import _, api, fields, models

logger = getLogger(__name__)


class Report(models.Model):
    _inherit = "ir.actions.report"

    use_front_cover = fields.Boolean(
        default=False, help="Use a front cover when rendering the PDF report."
    )
    use_back_cover = fields.Boolean(
        default=False, help="Use a back cover when rendering the PDF report."
    )

    front_cover_overlap = fields.Boolean(
        default=False,
        string="Overlap Front Cover",
        help="When set, the front cover of the report will overlap with the "
        "contents of the first page of the report. This is useful to include "
        "some information of the report in the front cover.",
    )
    back_cover_overlap = fields.Boolean(
        default=False,
        string="Overlap Back Cover",
        help="When set, the back cover of the report will overlap with the "
        "contents of the last page of the report. This is useful to include "
        "some information of the report in the back cover.",
    )

    front_cover_pdf = fields.Binary(
        string="Front Cover PDF",
        help="Upload an PDF file to use as a front cover on this report.",
    )
    back_cover_pdf = fields.Binary(
        string="Back Cover PDF",
        help="Upload an PDF file to use as a back cover on this report.",
    )

    @api.model
    def pdf_check_pages(self, num_pages, front=True):
        if num_pages < 1:
            if front:
                logger.error(_("Your front cover PDF does not contain any pages."))
            else:
                logger.error(_("Your back cover PDF does not contain any pages."))
            return False
        elif num_pages > 1:
            if front:
                logger.info(
                    _(
                        "Your front cover PDF contains more than one page, "
                        "all but the first one will be ignored."
                    )
                )
            else:
                logger.info(
                    _(
                        "Your back cover PDF contains more than one page, "
                        "all but the first one will be ignored."
                    )
                )
        return True

    def load_covers(
        self, report_sudo, front_cover, back_cover, use_front_cover, use_back_cover
    ):
        if use_front_cover:
            front_cover_pdf = self.front_cover_pdf or report_sudo.front_cover_pdf
            if front_cover_pdf:
                front_cover = b64decode(front_cover_pdf)
        if use_back_cover:
            back_cover_pdf = self.back_cover_pdf or report_sudo.back_cover_pdf
            if back_cover_pdf:
                back_cover = b64decode(back_cover_pdf)
        return front_cover, back_cover

    @api.model
    def load_cover_pdfs(self, front_cover, back_cover, use_front_cover, use_back_cover):
        pdf_front_cover = False
        pdf_back_cover = False
        if use_front_cover:
            try:
                pdf_front_cover = PdfFileReader(BytesIO(front_cover))
                if not pdf_front_cover:
                    use_front_cover = False
                    logger.error(_("No usable front cover found."))
            except Exception as e:
                use_front_cover = False
                logger.exception(_("Failed to load front cover: %s", e))
        if use_back_cover:
            try:
                pdf_back_cover = PdfFileReader(BytesIO(back_cover))
                if not pdf_back_cover:
                    use_back_cover = False
                    logger.error(_("No usable back cover found."))
            except Exception as e:
                use_back_cover = False
                logger.exception(_("Failed to load back cover: %s", e))
        return use_front_cover, pdf_front_cover, use_back_cover, pdf_back_cover

    @api.model
    def insert_cover_pages(
        self,
        pdf,
        pages,
        pdf_front_cover,
        pdf_back_cover,
        use_front_cover,
        use_back_cover,
        front_cover_overlap,
        back_cover_overlap,
    ):
        for index, page in enumerate(pages):
            report_page = pdf.addBlankPage(
                page.mediaBox.getWidth(), page.mediaBox.getHeight()
            )
            if index == 0 and use_front_cover:
                if not front_cover_overlap:
                    front_cover_page = report_page
                    front_cover_page.mergePage(pdf_front_cover.getPage(0))
                    report_page = pdf.addBlankPage(
                        page.mediaBox.getWidth(), page.mediaBox.getHeight()
                    )
                else:
                    report_page.mergePage(pdf_front_cover.getPage(0))
            if index == len(pages) - 1 and use_back_cover:
                if not back_cover_overlap:
                    back_cover_page = pdf.addBlankPage(
                        page.mediaBox.getWidth(), page.mediaBox.getHeight()
                    )
                    back_cover_page.mergePage(pdf_back_cover.getPage(0))
                else:
                    report_page.mergePage(pdf_back_cover.getPage(0))
            report_page.mergePage(page)

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
        result = super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )

        report_sudo = self._get_report(report_ref)
        front_cover = False
        back_cover = False
        use_front_cover = self.use_front_cover or report_sudo.use_front_cover
        use_back_cover = self.use_back_cover or report_sudo.use_back_cover
        front_cover_overlap = (
            self.front_cover_overlap or report_sudo.front_cover_overlap
        )
        back_cover_overlap = self.back_cover_overlap or report_sudo.back_cover_overlap
        if not use_front_cover and not use_back_cover:
            return result

        front_cover, back_cover = self.load_covers(
            report_sudo, front_cover, back_cover, use_front_cover, use_back_cover
        )
        if not front_cover and not back_cover:
            return result

        pdf = PdfFileWriter()
        (
            use_front_cover,
            pdf_front_cover,
            use_back_cover,
            pdf_back_cover,
        ) = self.load_cover_pdfs(
            front_cover, back_cover, use_front_cover, use_back_cover
        )
        if use_front_cover and not self.pdf_check_pages(
            pdf_front_cover.numPages, front=True
        ):
            use_front_cover = False
        if use_back_cover and not self.pdf_check_pages(
            pdf_back_cover.numPages, front=False
        ):
            use_back_cover = False

        pages = PdfFileReader(BytesIO(result)).pages
        self.insert_cover_pages(
            pdf,
            pages,
            pdf_front_cover,
            pdf_back_cover,
            use_front_cover,
            use_back_cover,
            front_cover_overlap,
            back_cover_overlap,
        )
        pdf_content = BytesIO()
        pdf.write(pdf_content)
        return pdf_content.getvalue()
