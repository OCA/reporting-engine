# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import lxml.html
from markupsafe import Markup

from odoo import api, fields, models
from odoo.tools.image import image_data_uri


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    include_company_images = fields.Boolean(
        help="If checked, company-level images will be shown in addition to "
        "report-specific images.",
    )
    report_positioned_image_ids = fields.Many2many(
        comodel_name="report.positioned.image",
        relation="ir_actions_report_positioned_image_rel",
        column1="report_id",
        column2="image_id",
        string="Report Images",
    )

    @staticmethod
    def _build_image_html(images):
        parts = []
        for image in images:
            image_content = image.get("image")
            if not image_content:
                continue
            style_parts = [
                "position: fixed",
                f"top: {image.get('pos_top', 5)}mm",
                f"left: {image.get('pos_left', 5)}mm",
                f"width: {image.get('width', 20)}mm",
                f"height: {image.get('height', 20)}mm",
            ]
            style = "; ".join(style_parts) + ";"
            data_uri = image_data_uri(image_content)
            # Use 'first-page' class from report_qweb_element_page_visibility
            # for images that should only appear on the first page
            css_class = "first-page" if image.get("first_page_only") else ""
            class_attr = f' class="{css_class}"' if css_class else ""
            parts.append(
                f'<div{class_attr} style="{style}">'
                f'<img src="{data_uri}" style="width: 100%; height: 100%;"/>'
                "</div>"
            )
        return Markup("".join(parts))

    def _insert_html_into_document(self, document, html_to_inject):
        if Markup("</body>") in document:
            return document.replace(
                Markup("</body>"), html_to_inject + Markup("</body>"), 1
            )
        if Markup("<body>") in document:
            return document.replace(
                Markup("<body>"), Markup("<body>") + html_to_inject, 1
            )
        return document + html_to_inject

    def _inject_images_into_header(self, header, image_configs):
        image_html = self._build_image_html(image_configs)
        return self._insert_html_into_document(header, image_html)

    def _get_condition_matches(self, res_ids, images):
        """Return {image id: set of matching res_ids} for the printed records."""
        printed_ids = [res_id for res_id in res_ids if res_id]
        if not printed_ids:
            return {}
        model = self.env[self.model]
        return {
            image.id: image._get_condition_matched_ids(model, printed_ids)
            for image in images
        }

    def _get_conditional_image_configs(self, res_id, images, matched_ids, **kwargs):
        if not res_id:
            return []
        return [
            self._image_to_config(image, **kwargs)
            for image in images
            if res_id in matched_ids.get(image.id, ())
        ]

    def _inject_conditional_images_into_header(
        self, header, res_ids, images, matched_ids
    ):
        """Inject each image into the header of the records matching its condition.

        ``_prepare_html`` merges the per-record headers into a single document,
        but keeps one child per rendered body under the
        'minimal_layout_report_headers' node; ``subst()`` then keeps only the
        child belonging to the body being printed. An image added to one of
        those children is therefore shown on every page of that record and on no
        other, and the 'first-page' class keeps working since ``subst()`` does
        run in the header document.

        Return None when the layout does not provide one header per rendered
        record, so that the caller can fall back to the bodies.
        """
        root = lxml.html.fromstring(
            header, parser=lxml.html.HTMLParser(encoding="utf-8")
        )
        containers = root.xpath("//*[@id='minimal_layout_report_headers']")
        if not containers:
            return None
        headers = containers[0].getchildren()
        if len(headers) != len(res_ids):
            return None
        injected = False
        for record_header, res_id in zip(headers, res_ids, strict=True):
            image_configs = self._get_conditional_image_configs(
                res_id, images, matched_ids
            )
            if not image_configs:
                continue
            record_header.append(
                lxml.html.fragment_fromstring(
                    str(self._build_image_html(image_configs)), create_parent="div"
                )
            )
            injected = True
        if not injected:
            return header
        return Markup(
            lxml.html.tostring(
                root,
                encoding="unicode",
                doctype=root.getroottree().docinfo.doctype or None,
            )
        )

    def _inject_conditional_images_into_bodies(
        self, bodies, res_ids, images, matched_ids
    ):
        """Inject each image into the bodies of the records matching its condition.

        Fallback for the layouts that carry no per-record header. wkhtmltopdf
        renders a fixed-position element of a body once, so the image only shows
        on the record's first page; 'first_page_only' is meaningless here as
        ``subst()`` never runs in a body.
        """
        new_bodies = []
        # ``res_ids`` holds a None for every body whose record could not be
        # identified, and is shorter than ``bodies`` when the layout carries no
        # 'article' node at all; zip() skips the former and the extension below
        # leaves the latter untouched.
        for body, res_id in zip(bodies, res_ids, strict=False):
            image_configs = self._get_conditional_image_configs(
                res_id, images, matched_ids, first_page_only=False
            )
            if image_configs:
                body = self._insert_html_into_document(
                    body, self._build_image_html(image_configs)
                )
            new_bodies.append(body)
        new_bodies.extend(bodies[len(new_bodies) :])
        return new_bodies

    @api.constrains("report_positioned_image_ids", "model")
    def _check_positioned_image_domains(self):
        """A report may only take images whose condition fits the model it renders."""
        for report in self:
            if not report.model or report.model not in self.env:
                continue
            model = self.env[report.model]
            for image in report.report_positioned_image_ids.filtered("domain"):
                image._validate_domain(model)

    @staticmethod
    def _image_to_config(image, first_page_only=None):
        return {
            "image": image.image,
            "pos_top": image.pos_top,
            "pos_left": image.pos_left,
            "width": image.width,
            "height": image.height,
            "first_page_only": (
                image.first_page_only if first_page_only is None else first_page_only
            ),
        }

    def _get_positioned_images(self):
        """Return the images configured for this report in the current company."""
        company = self.env.company
        images = self.report_positioned_image_ids.filtered(
            lambda img: img.company_id == company or not img.company_id
        )
        if self.include_company_images:
            images |= company.report_positioned_image_ids
        return images.filtered("image")

    def _is_conditional_image(self, image):
        """An image is conditional when it carries a condition to evaluate."""
        return bool(image.domain)

    def _get_positioned_image_configs(self):
        """Configs of the images injected into the (record-agnostic) header."""
        return [
            self._image_to_config(image)
            for image in self._get_positioned_images()
            if not self._is_conditional_image(image)
        ]

    def _get_conditional_positioned_images(self):
        """Images to place per record. Needs a model to evaluate them against."""
        if not self.model or self.model not in self.env:
            return self.env["report.positioned.image"]
        return self._get_positioned_images().filtered(self._is_conditional_image)

    def _prepare_html(self, html, report_model=False):
        result = super()._prepare_html(html, report_model=report_model)
        if not isinstance(result, tuple):
            return result
        bodies, res_ids, header, footer, specific_paperformat_args = result
        image_configs = self._get_positioned_image_configs()
        if image_configs:
            header = self._inject_images_into_header(header, image_configs)
        conditional_images = self._get_conditional_positioned_images()
        if conditional_images:
            matched_ids = self._get_condition_matches(res_ids, conditional_images)
            new_header = self._inject_conditional_images_into_header(
                header, res_ids, conditional_images, matched_ids
            )
            if new_header is None:
                bodies = self._inject_conditional_images_into_bodies(
                    bodies, res_ids, conditional_images, matched_ids
                )
            else:
                header = new_header
        return bodies, res_ids, header, footer, specific_paperformat_args

    def _get_report_company(self, res_ids):
        if not res_ids or not self.model:
            return self.env.company
        model = self.env[self.model]
        if "company_id" not in model._fields:
            return self.env.company
        records = model.browse(res_ids).exists()
        companies = records.mapped("company_id")
        return companies[0] if len(companies) == 1 else self.env.company

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """Set company context so _get_positioned_image_configs uses the
        correct company.
        """
        company = self._get_report_company(res_ids)
        return super(IrActionsReport, self.with_company(company))._render_qweb_pdf(
            report_ref, res_ids, data
        )
