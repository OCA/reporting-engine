# © 2016 Therp BV <http://therp.nl>
# Copyright 2023 Onestein - Anjeel Haria
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import io
from base64 import b64decode
from logging import getLogger

from PIL import Image

from odoo import fields, models
from odoo.tools.binary import BinaryValue
from odoo.tools.pdf import PdfFileReader, PdfFileWriter, PdfReadError
from odoo.tools.safe_eval import safe_eval

logger = getLogger(__name__)

try:
    # we need this to be sure PIL has loaded PDF support
    from PIL import PdfImagePlugin  # noqa: F401
except ImportError:
    logger.error("ImportError: The PdfImagePlugin could not be imported")


class Report(models.Model):
    _inherit = "ir.actions.report"

    use_company_watermark = fields.Boolean(
        default=False,
        help="Use the pdf watermark defined globally in the company settings.",
    )
    pdf_watermark = fields.Binary(
        "Watermark", help="Upload an pdf file to use as an watermark on this report."
    )
    pdf_watermark_expression = fields.Char(
        "Watermark expression",
        help="An expression yielding the base64 "
        "encoded data to be used as watermark. \n"
        "You have access to variables `env` and `docs`",
    )

    def _get_watermark_company(self, docids, report_sudo):
        """Return the company to use for the company watermark.

        When printing a document in a multi-company environment, the
        watermark should match the company of the document being printed,
        not the company selected in the UI switcher.  Falls back to
        ``self.env.company`` when no document or no ``company_id`` field
        is available.
        """
        if docids:
            model_name = self.model or report_sudo.model
            docs = self.env[model_name].browse(docids)
            if docs and "company_id" in docs._fields and docs[:1].company_id:
                return docs[:1].company_id
        return self.env.company

    @staticmethod
    def pdf_has_usable_pages(numpages):
        if numpages < 1:
            logger.error("Your watermark pdf does not contain any pages")
            return False
        if numpages > 1:
            logger.debug(
                "Your watermark pdf contains more than one page, "
                "all but the first one will be ignored"
            )
        return True

    def _get_watermark_report(self, report_sudo):
        """Return the report record that holds watermark settings.

        Some modules (e.g. sale_pdf_quote_builder) redirect the original
        report to a ``_raw`` variant for rendering. The user configures
        the watermark on the *original* report, but at rendering time
        ``report_sudo`` points to the ``_raw`` copy which has no watermark
        settings.  This helper falls back to the original report when the
        rendered report's ``report_name`` ends with ``_raw``.
        """
        if (
            not report_sudo.pdf_watermark
            and not report_sudo.use_company_watermark
            and not report_sudo.pdf_watermark_expression
            and report_sudo.report_name
            and report_sudo.report_name.endswith("_raw")
        ):
            original_name = report_sudo.report_name[: -len("_raw")]
            original = (
                self.env["ir.actions.report"]
                .sudo()
                .search([("report_name", "=", original_name)], limit=1)
            )
            if original:
                return original
        return report_sudo

    def _get_watermark(self, res_ids, report_sudo):
        """Determine and return the raw watermark bytes, or None."""
        # Resolve the effective report that carries watermark settings
        report_sudo = self._get_watermark_report(report_sudo)

        watermark = None
        if report_sudo.pdf_watermark:
            # Binary fields in Odoo 20 return BinaryValue objects;
            # .content gives us the raw bytes directly.
            watermark = report_sudo.pdf_watermark.content
        elif report_sudo.use_company_watermark:
            company = self._get_watermark_company(res_ids, report_sudo)
            if company.pdf_watermark:
                watermark = company.pdf_watermark.content
        elif res_ids and report_sudo.pdf_watermark_expression:
            watermark = safe_eval(
                report_sudo.pdf_watermark_expression,
                {
                    "env": self.env,
                    "docs": self.env[report_sudo.model].browse(res_ids),
                },
            )
            if isinstance(watermark, BinaryValue):
                # e.g. a Binary field such as ``docs[:1].company_id.logo``
                watermark = watermark.content
            elif watermark:
                # Other expressions return base64-encoded strings
                watermark = b64decode(watermark)
        return watermark

    def _apply_watermark(self, pdf_content, watermark):
        """Apply a watermark to PDF content bytes.

        :param bytes pdf_content: The original PDF content.
        :param bytes watermark: The raw watermark data (PDF or image).
        :return: Watermarked PDF content as bytes, or original if unable.
        :rtype: bytes
        """
        pdf_watermark = None
        try:
            pdf_watermark = PdfFileReader(io.BytesIO(watermark))
        except (UnicodeDecodeError, PdfReadError):
            # let's see if we can convert this with pillow
            try:
                Image.init()
                image = Image.open(io.BytesIO(watermark))
                pdf_buffer = io.BytesIO()
                if image.mode != "RGB":
                    image = image.convert("RGB")
                resolution = image.info.get("dpi", self.paperformat_id.dpi or 90)
                if isinstance(resolution, tuple):
                    resolution = resolution[0]
                image.save(pdf_buffer, "pdf", resolution=resolution)
                pdf_watermark = PdfFileReader(pdf_buffer)
            except Exception:
                logger.exception("Failed to load watermark")

        if not pdf_watermark:
            logger.error("No usable watermark found, got %s...", watermark[:100])
            return pdf_content

        if not self.pdf_has_usable_pages(len(pdf_watermark.pages)):
            return pdf_content

        writer = PdfFileWriter()
        for page in PdfFileReader(io.BytesIO(pdf_content)).pages:
            watermark_page = writer.add_blank_page(
                float(abs(page.mediabox.width)),
                float(abs(page.mediabox.height)),
            )
            # Merge watermark first (at the bottom)
            watermark_page.merge_page(pdf_watermark.pages[0])
            # Merge content page on top
            # (transparent background allows watermark to show through)
            watermark_page.merge_page(page)

        output = io.BytesIO()
        writer.write(output)
        return output.getvalue()

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        collected_streams = super()._render_qweb_pdf_prepare_streams(
            report_ref, data, res_ids=res_ids
        )
        report_sudo = self._get_report(report_ref)
        watermark = self._get_watermark(res_ids, report_sudo)
        if not watermark:
            return collected_streams

        # Apply watermark to each stream
        for stream_data in collected_streams.values():
            # Streams reloaded from a saved attachment ("attachment_use") were
            # already watermarked when first rendered
            if stream_data.get("attachment") and report_sudo.attachment_use:
                continue
            if stream_data.get("stream"):
                original = stream_data["stream"].getvalue()
                watermarked = self._apply_watermark(original, watermark)
                stream_data["stream"] = io.BytesIO(watermarked)

        return collected_streams
