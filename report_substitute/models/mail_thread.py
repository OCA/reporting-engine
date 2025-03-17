# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class MailThread(models.AbstractModel):
    _inherit = "mail.thread"

    def message_post_with_source(
        self,
        source_ref,
        render_values=None,
        message_type="notification",
        subtype_xmlid=False,
        subtype_id=False,
        **kwargs,
    ):
        template, view = self._get_source_from_ref(source_ref)
        if template and template.report_template_ids and self.ids:
            new_report_template_ids = [
                report.get_substitution_report(self.ids).id
                for report in template.report_template_ids
            ]
            return super(
                MailThread,
                self.with_context(default_report_template_ids=new_report_template_ids),
            ).message_post_with_source(
                source_ref,
                render_values,
                message_type,
                subtype_xmlid,
                subtype_id,
                **kwargs,
            )
        return super().message_post_with_source(
            source_ref,
            render_values,
            message_type,
            subtype_xmlid,
            subtype_id,
            **kwargs,
        )
