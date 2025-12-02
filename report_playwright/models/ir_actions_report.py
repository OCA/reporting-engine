import io
import logging
import os
import tempfile
import time
from urllib.parse import urlparse
from collections import OrderedDict

from PIL import Image

from odoo import _, api, fields, models
from odoo.exceptions import AccessError, UserError
from odoo.http import request
from odoo.tools import config
from odoo.tools.safe_eval import safe_eval

_logger = logging.getLogger(__name__)

playwright_state = "install"

try:
    from playwright.sync_api import Error, sync_playwright

    with sync_playwright() as p:
        try:
            p.chromium.connect(
                f"{os.environ.get('PLAYWRIGHT_SERVER_URL', 'ws://playwright:3000')}",
                timeout=os.environ.get("PLAYWRIGHT_CONNECTIVITY_TIMEOUT", 500),
            )
            _logger.info("Connected to Playwright successfuly")
        except Error as e:
            _logger.info(f"Cannot connect to playwright server {e.message}")
            raise Exception from e
except (ModuleNotFoundError, Exception) as e:
    _logger.info("You need playwright to print a pdf version of the reports.")
else:
    playwright_state = "ok"
    _logger.info("Will use the playwright library to print")


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("playwright-pdf", "playwright")],
        ondelete={"playwright-pdf": "cascade"},
    )

    @api.model
    def _build_playwright_options(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        header_content=None,
        footer_content=None,
    ):
        options = {
            "margin": {},
            "format": None,
            "sandbox": False,
            "landscape": False,
            "cookies": [],
        }

        if (
            landscape is None
            and specific_paperformat_args
            and specific_paperformat_args.get("data-report-landscape")
        ):
            landscape = specific_paperformat_args.get("data-report-landscape")

        # Passing the cookie to playwright in order to resolve internal links.
        if request and request.db:
            base_url = self._get_report_url()
            domain = urlparse(base_url).hostname
            options["cookies"] = [
                {
                    "name": "session_id",
                    "value": request.session.sid,
                    "domain": domain,
                    "httpOnly": True,
                    "expires": -1,
                    "path": "/",
                }
            ]

        if paperformat_id:
            if paperformat_id.format and paperformat_id.format != "custom":
                options["format"] = paperformat_id.format

            if specific_paperformat_args and specific_paperformat_args.get(
                "data-report-margin-top"
            ):
                options["margin"]["top"] = str(
                    specific_paperformat_args["data-report-margin-top"]
                )
            else:
                options["margin"]["top"] = str(paperformat_id.margin_top)

            options["margin"]["left"] = str(paperformat_id.margin_left)

            if specific_paperformat_args and specific_paperformat_args.get(
                "data-report-margin-bottom"
            ):
                options["margin"]["bottom"] = str(
                    specific_paperformat_args["data-report-margin-bottom"]
                )
            else:
                options["margin"]["bottom"] = str(paperformat_id.margin_bottom)

            options["margin"]["right"] = str(paperformat_id.margin_right)

            if not landscape and paperformat_id.orientation:
                options["landscape"] = str(paperformat_id.orientation) == "Landscape"

        if "landscape" not in options:
            options["landscape"] = landscape

        if header_content:
            options["headerTemplate"] = header_content

        if footer_content:
            options["footerTemplate"] = footer_content

        return options

    @api.model
    def _run_playwright(
        self,
        url,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
    ):
        paperformat_id = (
            self._get_report(report_ref).get_paperformat()
            if report_ref
            else self.get_paperformat()
        )

        temporary_files = []

        print_options = self._build_playwright_options(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            header_content=header,
            footer_content=footer,
        )

        prefix = "report.body.tmp."
        pdf_output_fd, pdf_output_path = tempfile.mkstemp(suffix=".pdf", prefix=prefix)
        os.close(pdf_output_fd)
        temporary_files.append(pdf_output_path)

        try:
            with sync_playwright() as p:
                browser = p.chromium.connect(
                    f"{os.environ.get('PLAYWRIGHT_SERVER_URL', 'ws://playwright:3000')}"
                )
                b_context = browser.new_context()
                b_context.add_cookies(print_options["cookies"])
                page = b_context.new_page()
                page.goto(url)
                page.pdf(
                    header_template=print_options["headerTemplate"],
                    footer_template=print_options["headerTemplate"],
                    format=print_options["format"],
                    margin=print_options["margin"],
                    landscape=print_options["landscape"],
                    path=pdf_output_path,
                )
        except Exception:
            raise

        pdf_streams = []
        with open(pdf_output_path, "rb") as pdf_doc:
            pdf_content = pdf_doc.read()
            pdf_streams.append(pdf_content)

        for file in temporary_files:
            try:
                os.unlink(file)
            except OSError:
                _logger.error("Error when trying to remove file %s" % file)

        return pdf_streams

    @api.model
    def get_playwright_state(self):
        """Get the current state of wkhtmltopdf: install, ok, upgrade, workers or broken.
        * install: Starting state.
        * upgrade: The binary is an older version (< 0.12.0).
        * ok: A binary was found with a recent version (>= 0.12.0).
        * workers: Not enough workers found to perform the pdf rendering process (< 2 workers).
        * broken: A binary was found but not responding.

        :return: playwright_state
        """
        return playwright_state

    def _render_playwright_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        if not data:
            data = {}
        data.setdefault("report_type", "pdf")

        # access the report details with sudo() but evaluation context as current user
        report_sudo = self._get_report(report_ref)

        collected_streams = OrderedDict()

        # Fetch the existing attachments from the database for later use.
        # Reload the stream from the attachment in case of 'attachment_use'.
        if res_ids:
            records = self.env[report_sudo.model].browse(res_ids)
            for record in records:
                stream = None
                attachment = None
                if report_sudo.attachment:
                    attachment = report_sudo.retrieve_attachment(record)

                    # Extract the stream from the attachment.
                    if attachment and report_sudo.attachment_use:
                        stream = io.BytesIO(attachment.raw)

                        # Ensure the stream can be saved in Image.
                        if attachment.mimetype.startswith("image"):
                            img = Image.open(stream)
                            new_stream = io.BytesIO()
                            img.convert("RGB").save(new_stream, format="pdf")
                            stream.close()
                            stream = new_stream

                collected_streams[record.id] = {
                    "stream": stream,
                    "attachment": attachment,
                }

        # Call 'wkhtmltopdf' to generate the missing streams.
        res_ids_wo_stream = [
            res_id
            for res_id, stream_data in collected_streams.items()
            if not stream_data["stream"]
        ]
        is_playwright_needed = not res_ids or res_ids_wo_stream

        if is_playwright_needed:
            if self.get_playwright_state() == "install":
                # playwright is not installed
                # the call should be catched before (cf /report/check_wkhtmltopdf) but
                # if get_pdf is called manually (email template), the check could be
                # bypassed
                raise UserError(
                    _(
                        "Unable to find playwright on this system. The PDF can not be created."
                    )
                )

            # Disable the debug mode in the PDF rendering in order to not split
            # the assets bundle
            # into separated files to load. This is done because of an issue in wkhtmltopdf
            # failing to load the CSS/Javascript resources in time.
            # Without this, the header/footer of the reports randomly disappear
            # because the resources files are not loaded in time.
            # https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2083
            additional_context = {"debug": False}

            # As the assets are generated during the same transaction as the rendering of the
            # templates calling them, there is a scenario where the assets are unreachable: when
            # you make a request to read the assets while the transaction creating
            # them is not done.
            # Indeed, when you make an asset request, the controller has to read the
            # `ir.attachment`
            # table.
            # This scenario happens when you want to print a PDF report for the first
            # time, as the
            # assets are not in cache and must be generated. To workaround this issue,
            # we manually
            # commit the writes in the `ir.attachment` table. It is done thanks
            # to a key in the context.
            if (
                not config["test_enable"]
                and "commit_assetsbundle" not in self.env.context
            ):
                additional_context["commit_assetsbundle"] = True

            html = self.with_context(**additional_context)._render_qweb_html(
                report_ref, res_ids_wo_stream, data=data
            )[0]
            if "path" not in data:
                report_xml_id = (
                    report_ref.xml_id if hasattr(report_ref, "xml_id") else report_ref
                )
                data["path"] = (
                    f"/report/html/{report_xml_id}/{','.join([str(r) for r in res_ids])}"
                )
            url = self._get_report_url() + data["path"]

            (
                bodies,
                html_ids,
                header,
                footer,
                specific_paperformat_args,
            ) = self.with_context(**additional_context)._prepare_html(
                html, report_model=report_sudo.model
            )

            if report_sudo.attachment and set(res_ids_wo_stream) != set(html_ids):
                raise UserError(
                    _(
                        "The report's template %r is wrong, "
                        "please contact your "
                        "administrator. \n\n"
                        "Can not separate file to save as attachment because the report's "
                        "template does not contains the"
                        " attributes 'data-oe-model' and 'data-oe-id' on the div with "
                        "'article' classname.",
                        self.name,
                    )
                )

            pdf_streams = self._run_playwright(
                url,
                report_ref=report_ref,
                header=header,
                footer=footer,
                landscape=self._context.get("landscape"),
                specific_paperformat_args=specific_paperformat_args,
            )

            # Printing a PDF report without any records. The content could be returned directly.
            if not res_ids:
                return {
                    False: {
                        "stream": io.BytesIO(pdf_streams[0]),
                        "attachment": None,
                    }
                }

            # Split the pdf for each record using the PDF outlines.

            # Only one record: append the whole PDF.
            if len(res_ids_wo_stream) == 1:
                collected_streams[res_ids_wo_stream[0]]["stream"] = pdf_streams[0]
                return collected_streams

            # In case of multiple docs, we need to split the pdf according the records.
            # To do so, we split the pdf based on top outlines computed by wkhtmltopdf.
            # An outline is a <h?> html tag found on the document. To retrieve this table,
            # we look on the pdf structure using pypdf to compute the outlines_pages from
            # the top level heading in /Outlines.
            html_ids_wo_none = [x for x in html_ids if x]
            if len(res_ids_wo_stream) > 1 and set(res_ids_wo_stream) == set(
                html_ids_wo_none
            ):
                for i in range(len(res_ids)):
                    collected_streams[res_ids[i]]["stream"] = pdf_streams[i]

                return collected_streams

            collected_streams[False] = {"stream": pdf_streams[0], "attachment": None}

        return collected_streams

    @api.model
    def _render_playwright_pdf(self, report_ref, res_ids, data=None):
        if not data:
            data = {}
        if isinstance(res_ids, int):
            res_ids = [res_ids]
        data.setdefault("report_type", "pdf")
        # In case of test environment without enough workers to perform calls to wkhtmltopdf,
        # fallback to render_html.
        if (config["test_enable"] or config["test_file"]) and not self.env.context.get(
            "force_report_rendering"
        ):
            return self._render_qweb_html(report_ref, res_ids, data=data)

        collected_streams = self._render_playwright_pdf_prepare_streams(
            report_ref, data, res_ids=res_ids
        )

        # access the report details with sudo() but keep evaluation context as current user
        report_sudo = self._get_report(report_ref)

        # Generate the ir.attachment if needed.
        if report_sudo.attachment:
            attachment_vals_list = []
            for res_id, stream_data in collected_streams.items():
                # An attachment already exists.
                if stream_data["attachment"]:
                    continue

                # if res_id is false
                # we are unable to fetch the record, it won't be saved as
                # we can't split the documents unambiguously
                if not res_id:
                    _logger.warning(
                        "These documents were not saved as an attachment "
                        "because the template of %s doesn't "
                        "have any headers seperating different "
                        "instances of it. If you want it saved,"
                        "please print the documents separately",
                        report_sudo.report_name,
                    )
                    continue
                record = self.env[report_sudo.model].browse(res_id)
                attachment_name = safe_eval(
                    report_sudo.attachment, {"object": record, "time": time}
                )

                # Unable to compute a name for the attachment.
                if not attachment_name:
                    continue

                attachment_vals_list.append(
                    {
                        "name": attachment_name,
                        "raw": stream_data["stream"].getvalue(),
                        "res_model": report_sudo.model,
                        "res_id": record.id,
                        "type": "binary",
                    }
                )

            if attachment_vals_list:
                attachment_names = ", ".join(x["name"] for x in attachment_vals_list)
                try:
                    self.env["ir.attachment"].create(attachment_vals_list)
                except AccessError:
                    _logger.info(
                        "Cannot save PDF report %r attachments for user %r",
                        attachment_names,
                        self.env.user.display_name,
                    )
                else:
                    _logger.info(
                        "The PDF documents %r are now saved in the database",
                        attachment_names,
                    )

        # Merge all streams together for a single record.
        streams_to_merge = [
            x["stream"] for x in collected_streams.values() if x["stream"]
        ]
        if len(streams_to_merge) == 1:
            pdf_content = streams_to_merge[0]
        else:
            with self._merge_pdfs(streams_to_merge) as pdf_merged_stream:
                pdf_content = pdf_merged_stream

        if res_ids:
            _logger.info(
                "The PDF report has been generated for model: %s, records %s.",
                report_sudo.model,
                str(res_ids),
            )

        return pdf_content, "pdf"
