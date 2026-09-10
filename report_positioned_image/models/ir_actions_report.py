# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import fields, models
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

    def _insert_html_into_header(self, header, html_to_inject):
        if Markup("</body>") in header:
            return header.replace(
                Markup("</body>"), html_to_inject + Markup("</body>"), 1
            )
        if Markup("<body>") in header:
            return header.replace(
                Markup("<body>"), Markup("<body>") + html_to_inject, 1
            )
        return header + html_to_inject

    def _inject_images_into_header(self, header, image_configs):
        image_html = self._build_image_html(image_configs)
        return self._insert_html_into_header(header, image_html)

    def _get_positioned_image_configs(self):
        company = self.env.company
        images = self.report_positioned_image_ids.filtered(
            lambda img: img.company_id == company or not img.company_id
        )
        if self.include_company_images:
            images |= company.report_positioned_image_ids
        return [
            {
                "image": img.image,
                "pos_top": img.pos_top,
                "pos_left": img.pos_left,
                "width": img.width,
                "height": img.height,
                "first_page_only": img.first_page_only,
            }
            for img in images
            if img.image
        ]

    def _prepare_html(self, html, report_model=False):
        image_configs = self._get_positioned_image_configs()
        if not image_configs:
            return super()._prepare_html(html, report_model=report_model)
        result = super()._prepare_html(html, report_model=report_model)
        if not isinstance(result, tuple):
            return result
        bodies, res_ids, header, footer, specific_paperformat_args = result
        header = self._inject_images_into_header(header, image_configs)
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
