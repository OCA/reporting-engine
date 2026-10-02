from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class ReportPrintedConfig(models.Model):
    """
    Configuration model to control the behavior of the printed flag mechanism.
    This model allows defining, per model and company:
    - Which reports trigger the printed flag
    - Optional domain conditions per report
    - Whether to generate logs
    - Whether to compute printed report names
    Each configuration is unique per (company, model).
    """

    _name = "report.printed.config"
    _description = "Report Printed Flag Configuration"
    _order = "company_id, model_id, id"
    _rec_name = "display_name"

    name = fields.Char(
        required=True,
        translate=True,
    )
    active = fields.Boolean(
        default=True,
    )
    company_id = fields.Many2one(
        comodel_name="res.company",
        required=True,
        default=lambda self: self.env.company,
        ondelete="cascade",
    )
    model_id = fields.Many2one(
        "ir.model",
        required=True,
        ondelete="cascade",
        domain="[('transient', '=', False), ('id', 'in', allowed_model_ids)]",
    )
    allowed_model_ids = fields.Many2many(
        "ir.model",
        default=lambda self: self._default_allowed_models(),
    )
    model = fields.Char(
        related="model_id.model",
        store=True,
        readonly=True,
        string="Technical Model",
    )
    line_ids = fields.One2many(
        "report.printed.config.line",
        "config_id",
        string="Report Rules",
    )
    note = fields.Text()
    display_name = fields.Char(
        compute="_compute_display_name",
        store=True,
    )
    report_printed_log_active = fields.Boolean(
        string="Enable Printed Logs",
        default=True,
    )
    report_printed_names_active = fields.Boolean(
        string="Enable Printed Report Names",
        default=True,
    )

    _sql_constraints = [
        (
            "report_printed_config_unique_model_company",
            "unique(company_id, model_id)",
            "Only one configuration per model and company is allowed.",
        ),
    ]

    def _default_allowed_models(self):
        """
        Return models that contain a ``printed`` field.
        This is used to restrict configuration only to compatible models.
        """
        return (
            self.env["ir.model"]
            .search(
                [
                    ("field_id.name", "=", "printed"),
                ]
            )
            .ids
        )

    @api.depends("name", "company_id", "model_id")
    def _compute_display_name(self):
        """
        Compute a human-readable name combining:
        - Configuration name
        - Company
        - Model
        """
        for record in self:
            parts = [
                record.name,
                record.company_id.display_name if record.company_id else False,
                record.model_id.name if record.model_id else False,
            ]
            record.display_name = " - ".join([p for p in parts if p])

    @api.constrains("model_id")
    def _check_model_has_printed(self):
        """
        Ensure that the selected model contains a ``printed`` field.
        Prevents misconfiguration on unsupported models.
        """
        for record in self:
            if not record.model_id:
                continue
            has_printed = self.env["ir.model.fields"].search_count(
                [
                    ("model_id", "=", record.model_id.id),
                    ("name", "=", "printed"),
                ]
            )
            if not has_printed:
                raise ValidationError(_("Selected model must have a 'printed' field."))

    @api.constrains("line_ids", "model_id")
    def _check_report_model_consistency(self):
        """
        Ensure that all configured reports belong to the selected model.
        Prevents assigning reports from unrelated models.
        """
        for record in self:
            if not record.model_id:
                continue
            invalid_lines = record.line_ids.filtered(
                lambda line, record=record: line.report_id.model != record.model
            )
            if invalid_lines:
                raise ValidationError(
                    _("All selected reports must belong to model '%s'.") % record.model
                )

    @api.constrains(
        "report_printed_names_active",
        "report_printed_log_active",
    )
    def _check_flags(self):
        """
        Ensure consistency between feature flags.
        Printed report names require logs to be enabled.
        """
        for rec in self:
            if rec.report_printed_names_active and not rec.report_printed_log_active:
                raise ValidationError(
                    _("You must enable logs to use printed report names.")
                )

    @api.onchange("report_printed_names_active")
    def _onchange_report_names_active(self):
        """
        Auto-enable logs when report names feature is activated.
        """
        if self.report_printed_names_active:
            self.report_printed_log_active = True

    @api.onchange("report_printed_log_active")
    def _onchange_report_log_active(self):
        """
        Disable report names feature when logs are disabled.
        """
        if not self.report_printed_log_active:
            self.report_printed_names_active = False


class ReportPrintedConfigLine(models.Model):
    """
    Configuration line defining rules per report.
    Each line represents:
    - A specific report
    - An optional domain condition to filter records
    The domain is evaluated at runtime before applying
    the printed flag.
    """

    _name = "report.printed.config.line"
    _description = "Printed Config Line"

    config_id = fields.Many2one(
        "report.printed.config",
        required=True,
        ondelete="cascade",
    )
    report_id = fields.Many2one(
        "ir.actions.report",
        required=True,
    )

    domain = fields.Char()
