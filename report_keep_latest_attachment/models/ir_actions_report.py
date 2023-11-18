# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    keep_latest_attachment = fields.Boolean()

    def _post_pdf(self, save_in_attachment, pdf_content=None, res_ids=None):
        ir_attachment_obj = self.env["ir.attachment"]
        ids = []
        if self.keep_latest_attachment:
            if res_ids:
                ids = res_ids
            if save_in_attachment:
                ids = list(save_in_attachment.keys())
            if ids:
                record = self.env[self.model_id.model].browse(ids)
                domain = [
                    ("res_model", "=", record._name),
                    ("res_id", "=", str(record.id)),
                    ("res_name", "ilike", "%{}%".format(record.name)),
                    ("name", "ilike", "%.pdf"),
                ]
                attachments = ir_attachment_obj.search(domain, order="create_date desc")

                if len(attachments) > 1:
                    attachments_to_delete = attachments[1:]
                    if attachments_to_delete:
                        attachments_to_delete.unlink()

        return super(IrActionsReport, self)._post_pdf(
            save_in_attachment, pdf_content, res_ids
        )
