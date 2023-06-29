# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

import base64

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from odoo.tools.safe_eval import safe_eval

# Define all supported report_type
REPORT_TYPES_FUNC = {
    "qweb-pdf": "_render_qweb_pdf",
    "qweb-text": "_render_qweb_text",
    "qweb-xml": "_render_qweb_xml",
    "csv": "_render_csv",
    "excel": "render_excel",
    "xlsx": "_render_xlsx",
}


class ReportAsync(models.Model):
    _name = "report.async"
    _description = "Report Async"

    action_id = fields.Many2one(
        comodel_name="ir.actions.act_window",
        string="Reports",
        required=True,
    )
    allow_async = fields.Boolean(
        default=False,
        help="This is not automatic field, please check if you want to allow "
        "this report in background process",
    )
    name = fields.Char(
        string="Name",
        related="action_id.display_name",
    )
    email_notify = fields.Boolean(
        string="Email Notification",
        help="Send email with link to report, when it is ready",
    )
    group_ids = fields.Many2many(
        string="Groups",
        comodel_name="res.groups",
        help="Only user in selected groups can use this report."
        "If left blank, everyone can use",
    )
    job_ids = fields.Many2many(
        comodel_name="queue.job",
        compute="_compute_job",
        help="List all jobs related to this running report",
    )
    job_status = fields.Selection(
        selection=[
            ("pending", "Pending"),
            ("enqueued", "Enqueued"),
            ("started", "Started"),
            ("done", "Done"),
            ("failed", "Failed"),
        ],
        compute="_compute_job",
        help="Latest Job Status",
    )
    job_info = fields.Text(
        compute="_compute_job",
        help="Latest Job Error Message",
    )
    file_ids = fields.Many2many(
        comodel_name="ir.attachment",
        compute="_compute_file",
        help="List all files created by this report background process",
    )

    def _compute_job(self):
        for rec in self:
            rec.job_ids = (
                self.sudo()
                .env["queue.job"]
                .search(
                    [
                        ("func_string", "like", "report.async(%s,)" % rec.id),
                        ("user_id", "=", self._uid),
                    ],
                    order="id desc",
                )
            )
            rec.job_status = rec.job_ids[0].sudo().state if rec.job_ids else False
            rec.job_info = rec.job_ids[0].sudo().exc_info if rec.job_ids else False

    def _compute_file(self):
        files = self.env["ir.attachment"].search(
            [
                ("res_model", "=", "report.async"),
                ("res_id", "in", self.ids),
                ("create_uid", "=", self._uid),
            ],
            order="id desc",
        )
        for rec in self:
            rec.file_ids = files.filtered(lambda l: l.res_id == rec.id)

    def run_now(self):
        self.ensure_one()
        action = self.env.ref(self.action_id.xml_id)
        result = action.sudo().read()[0]
        ctx = safe_eval(result.get("context", {}))
        ctx.update({"async_process": False})
        result["context"] = ctx
        return result

    def run_async(self):
        self.ensure_one()
        if not self.allow_async:
            raise UserError(_("Background process not allowed."))
        action = self.env.ref(self.action_id.xml_id)
        result = action.sudo().read()[0]
        ctx = safe_eval(result.get("context", {}))
        ctx.update({"async_process": True})
        result["context"] = ctx
        return result

    def view_files(self):
        self.ensure_one()
        action = self.env.ref("report_async.action_view_files")
        result = action.sudo().read()[0]
        result["domain"] = [("id", "in", self.file_ids.ids)]
        return result

    def view_jobs(self):
        self.ensure_one()
        action = self.env.ref("queue_job.action_queue_job")
        result = action.sudo().read()[0]
        result["domain"] = [("id", "in", self.job_ids.ids)]
        result["context"] = {}
        return result

    @api.model
    def run_report(self, docids, data, report_id, user_id):
        report = self.env["ir.actions.report"].browse(report_id)
        func = REPORT_TYPES_FUNC[report.report_type]
        # Run report
        out_file, file_ext = getattr(report, func)(report.xml_id, docids, data)
        out_file = base64.b64encode(out_file)
        out_name = "{}.{}".format(report.name, file_ext)
        # Save report to attachment
        attachment = (
            self.env["ir.attachment"]
            .sudo()
            .create(
                {
                    "name": out_name,
                    "datas": out_file,
                    "type": "binary",
                    "res_model": "report.async",
                    "res_id": self.id,
                }
            )
        )
        self._cr.execute(
            """
            UPDATE ir_attachment SET create_uid = %s, write_uid = %s
            WHERE id = %s""",
            (self._uid, self._uid, attachment.id),
        )
        # Send email
        if self.email_notify:
            self._send_email(attachment)

    def _send_email(self, attachment):
        template = self.env.ref("report_async.async_report_delivery")
        template.send_mail(
            attachment.id,
            email_layout_xmlid="mail.mail_notification_light",
            force_send=False,
        )
