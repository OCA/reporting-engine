from odoo import models
from odoo.tools.safe_eval import safe_eval


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf(self, report_ref, res_ids=None, data=None):
        """
        Override PDF rendering to hook into the report generation process.
        Before delegating to the standard rendering logic, this method applies
        the printed flag mechanism on the target records, based on the
        configuration defined in ``report.printed.config``.
        :param report_ref: External ID or report reference
        :param res_ids: Record IDs for which the report is generated
        :param data: Optional data payload
        :return: PDF binary content (standard Odoo behavior)
        """
        report = self._get_report(report_ref)
        self._apply_printed_flag(report, res_ids)
        return super()._render_qweb_pdf(
            report_ref,
            res_ids=res_ids,
            data=data,
        )

    def _apply_printed_flag(self, report, res_ids):
        """
        Apply the printed flag and optionally create log entries for records
        associated with a report execution.
        This method:
        - Identifies the target model from the report
        - Retrieves the corresponding records
        - Loads active configurations for the model and company
        - Matches the report against configured rules (lines)
        - Applies optional domain filtering per report
        - Sets ``printed = True`` when conditions are met
        - Creates log entries if enabled in configuration
        The logic is evaluated per record to ensure proper multi-company
        behavior and per-report rule enforcement.
        :param report: ir.actions.report record
        :param res_ids: list of record IDs
        :return: None
        """
        if not report or not res_ids:
            return
        model_name = report.model
        records = self.env[model_name].browse(res_ids).exists()
        # Skip if model does not support printed flag
        if not records or "printed" not in records._fields:
            return
        company_ids = []
        if "company_id" in records._fields:
            company_ids = records.mapped("company_id").ids
        domain = [
            ("active", "=", True),
            ("model", "=", model_name),
        ]
        if company_ids:
            domain.append(("company_id", "in", company_ids))
        # Load configurations for model and companies involved
        configs = self.env["report.printed.config"].sudo().search(domain)
        if not configs:
            return
        log_vals = []
        for record in records:
            config = configs.filtered(
                lambda conf, record=record: not conf.company_id
                or (
                    "company_id" in record._fields
                    and conf.company_id == record.company_id
                )
            )[:1]
            if not config:
                continue
            line = config.line_ids.filtered(
                lambda conf_line: conf_line.report_id == report
            )[:1]
            if not line:
                continue
            matches_domain = not line.domain or record.filtered_domain(
                safe_eval(line.domain)
            )
            if not matches_domain:
                continue
            # Mark as printed
            record.printed = True
            # Collect logs for batch creation
            if config.report_printed_log_active:
                vals = {
                    "res_model": model_name,
                    "res_id": record.id,
                    "report_id": report.id,
                    "user_id": self.env.user.id,
                    "name": getattr(
                        record,
                        "name",
                        record.display_name,
                    ),
                }
                if "company_id" in record._fields:
                    vals["company_id"] = record.company_id.id
                log_vals.append(vals)
        if log_vals:
            self.env["report.printed.log"].sudo().create(log_vals)
