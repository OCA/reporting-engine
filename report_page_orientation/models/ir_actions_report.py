# Copyright 2022 Sunflower IT <https://www.sunflowerweb.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import io
import logging
import tempfile
from copy import deepcopy

import lxml.html
from lxml import etree
from odoo import api, models
from PyPDF2 import PdfFileReader, PdfFileWriter

_logger = logging.getLogger(__name__)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        args = super(IrActionsReport, self)._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        # args.remove("--quiet")
        # args += ["--debug-javascript"]
        toc_file = self.env.context.get("report_page_orientation_toc_file")
        if toc_file:
            args += ["--dump-outline", toc_file]
        return args

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):

        # loop bodies
        _logger.info("Number of bodies: %s", len(bodies))

        # check if any body has any 'rotated-page-orientation' blocks
        new_bodies = []
        bodies_with_rotation = 0
        for i, body in enumerate(bodies):
            root = lxml.html.fromstring(body)
            match_klass = (
                "//div[contains(concat(' ', normalize-space(@class), ' '), ' {} ')]"
            )
            section_elements = root.xpath(
                match_klass.format("rotated-page-orientation")
            )
            if not section_elements:
                new_bodies.append(body)
                continue

            # if yes, pre-render these sections separately, to see how many pages they are
            _logger.info("Body %s: %s sections", i, len(section_elements))
            bodies_with_rotation += 1
            sections = []
            for section_element in section_elements:
                content = lxml.html.tostring(section_element, encoding="unicode")
                section_pdf_content = super(IrActionsReport, self)._run_wkhtmltopdf(
                    [content],
                    header=header,
                    footer=footer,
                    landscape=not landscape,
                    specific_paperformat_args=specific_paperformat_args,
                    set_viewport_size=set_viewport_size,
                )
                section_pdf_stream = io.BytesIO(section_pdf_content)
                section_pdf = PdfFileReader(section_pdf_stream)
                section_pdf_pages = section_pdf.getNumPages()
                sections.append(
                    {
                        "num_pages": section_pdf_pages,
                        "element": section_element,
                        "content": content,
                    }
                )

            # within the body, replace such a section with a number of page breaks equal
            #     to each section that is in between. mark such a page break with a class. also
            #     mark the first one per section.
            for section in sections:
                placeholderpage = lxml.html.fromstring(
                    "<h1 style='page-break-before: always;'>PLACEHOLDER</h1>"
                )
                morepage = lxml.html.fromstring(
                    "<div style='page-break-before: always;'>MORE</div>"
                )
                page_break = lxml.html.fromstring(
                    "<div style='page-break-before: always;'/>"
                )
                element = section["element"]
                parent = element.getparent()
                parent.replace(element, placeholderpage)
                placeholderpage.addnext(page_break)
                num_pages = section["num_pages"]
                if num_pages > 1:
                    for i in range(num_pages - 1):
                        page_break.addprevious(deepcopy(morepage))
            if sections:
                body = lxml.html.tostring(root, encoding="unicode")
            new_bodies.append(body)

        # If no change, just return super.
        if not bodies_with_rotation:
            return super(IrActionsReport, self)._run_wkhtmltopdf(
                bodies,
                header=header,
                footer=footer,
                landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size,
            )

        # or: put 'h1' elements and generate a toc in XML, and get the page numbers from there.
        toc_file_fd, toc_file_path = tempfile.mkstemp(
            suffix=".xml", prefix="report.toc."
        )
        ret = super(
            IrActionsReport,
            self.with_context(report_page_orientation_toc_file=toc_file_path),
        )._run_wkhtmltopdf(
            new_bodies,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        toc_content = etree.parse(toc_file_path)
        root = toc_content.getroot()
        placeholder_pages = toc_content.findall("//*[@title='PLACEHOLDER']")
        for i, placeholder_page in enumerate(placeholder_pages):
            sections[i]["page"] = int(placeholder_page.attrib["page"])

        # now do a post rendering step to copy and paste the pages into the final pdf, replacing the dummy pages.
        pdf_stream = io.BytesIO(ret)
        input_pdf = PdfFileReader(pdf_stream)
        output_pdf = PdfFileWriter()
        input_pdf_pages = input_pdf.getNumPages()
        section_counter = 0
        input_page_counter = 0

        while input_page_counter < input_pdf_pages:
            if (section_counter < len(sections)) and sections[section_counter].get(
                "page", 0
            ) == input_page_counter + 1:
                footer_element = lxml.html.fromstring(footer)
                subst_elements = footer_element.xpath(
                    "//script[contains(text(), 'subst')]"
                )
                multi_footer = footer
                if subst_elements:
                    subst2 = lxml.html.fragment_fromstring(
                        """<script>
                        var origsubst = subst;
                        window.subst = function() {
                            var ret = origsubst();
                            var vars = {};
                            var x = document.location.search.substring(1).split('&');
                            for (var i in x) {
                                var z = x[i].split('=', 2);
                                vars[z[0]] = unescape(z[1]);
                                // sneaky modifications
                                if (z[0] == 'sitepage') {
                                    vars[z[0]] = parseInt(vars[z[0]]) + %d;
                                }
                                else if (z[0] == 'sitepages') {
                                    vars[z[0]] = %d;
                                }
                            }
                            var x = ['sitepage', 'sitepages', 'section', 'subsection', 'subsubsection'];
                            var z = {'sitepage': 'page', 'sitepages': 'topage'};
                            for (var i in x) {
                                var y = document.getElementsByClassName(z[x[i]] || x[i]);
                                for (var j=0; j<y.length; ++j) {
                                    y[j].textContent = vars[x[i]];
                                }
                            }
                            return ret;
                        };
                        </script>"""
                        % (input_page_counter, input_pdf_pages)
                    )
                    subst_elements[-1].addnext(subst2)
                    multi_footer = lxml.html.tostring(
                        footer_element, encoding="unicode"
                    )

                section = sections[section_counter]
                num_pages = section["num_pages"]
                section_pdf_content = super(IrActionsReport, self)._run_wkhtmltopdf(
                    [section["content"]],
                    header=header,
                    footer=multi_footer,
                    landscape=not landscape,
                    specific_paperformat_args=specific_paperformat_args,
                    set_viewport_size=set_viewport_size,
                )
                section_pdf_stream = io.BytesIO(section_pdf_content)
                section_pdf = PdfFileReader(section_pdf_stream)
                section_pdf_pages = section_pdf.getNumPages()
                assert section_pdf_pages == num_pages
                for j in range(0, section_pdf_pages):
                    output_pdf.addPage(section_pdf.getPage(j))
                section_counter += 1
                input_page_counter += num_pages
                continue
            page = input_pdf.getPage(input_page_counter)
            output_pdf.addPage(page)
            input_page_counter += 1
        with io.BytesIO() as _buffer:
            output_pdf.write(_buffer)
            return _buffer.getvalue()

        # unit-test this.
