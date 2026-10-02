from odoo import api, fields, models


class ReportPrintedMixin(models.AbstractModel):
    """
    Mixin providing printed flag tracking functionality.

    Any model inheriting from this mixin gains:
    - A ``printed`` Boolean field to mark records as printed
    - A ``printed_log_ids`` One2many relation to print logs
    - A ``printed_report_names`` Char field with computed printed report names
    - An ``action_view_printed_logs()`` method to view related logs

    This mixin works with the ``report_printed_flag`` configuration system:
    - Configuration defines which reports trigger the printed flag
    - Logs are created automatically when a configured report is generated
    - The ``printed_report_names`` field is computed from logs if enabled

    Extension modules simply inherit from this mixin:
        class MyModel(models.Model):
            _name = 'my.model'
            _inherit = ['my.model', 'report.printed.mixin']

    Note:
    - The model must have the ``printed`` field supported by its target reports
    - Requires the ``report_printed_flag`` module to be installed
    - Domain filtering on ``printed_log_ids`` is automatically handled via
      the ``Many2oneReference`` field on ``report.printed.log.res_id``
    """

    _name = "report.printed.mixin"
    _description = "Report Printed Mixin"

    printed = fields.Boolean(
        default=False,
        copy=False,
        index=True,
        help="Indicates whether at least one configured report has been printed "
        "for this record.",
    )

    printed_log_ids = fields.One2many(
        "report.printed.log",
        "res_id",
        # No explicit domain needed: ORM automatically injects
        # [('res_model', '=', self._name)] because res_id uses
        # Many2oneReference(model_field='res_model')
        string="Print Logs",
        help=(
            "Technical relation to printed logs using a generic reference pattern "
            "(res_model, res_id). Only logs related to this model type are included."
        ),
    )

    printed_report_names = fields.Char(
        compute="_compute_printed_report_names",
        store=True,
        string="Printed Reports Names",
        help=(
            "Comma-separated list of printed report names, computed from related "
            "printed logs. Only active if enabled in configuration."
        ),
    )

    @api.depends("printed_log_ids", "company_id")
    def _compute_printed_report_names(self):
        """
        Compute the list of printed report names for each record.

        The computation:
        1. Loads active configurations for the current model and companies
        2. Builds a lookup map (model, company) -> config
        3. For each record:
           - Checks if report names computation is enabled in config
           - Retrieves related printed logs
           - Extracts report names from logs
           - Removes duplicates while preserving order
           - Joins names into a comma-separated string

        Notes:
        - Uses ``display_name`` to ensure consistency with Odoo UI
        - Respects multi-company isolation
        - Skips computation if feature is disabled in configuration
        """
        Config = self.env["report.printed.config"]
        company_ids = list({rec.company_id.id for rec in self if rec.company_id})

        # Retrieve configurations for this model and all involved companies
        configs = Config.search(
            [
                ("model", "=", self._name),
                ("company_id", "in", company_ids),
            ]
        )

        # Build a lookup map for quick access: (model, company_id) -> config
        config_map = {(c.model, c.company_id.id): c for c in configs}

        for rec in self:
            # Get configuration for this record's company
            config = config_map.get((rec._name, rec.company_id.id))

            # Feature disabled or no configuration found
            if not config or not config.report_printed_names_active:
                rec.printed_report_names = False
                continue

            # Collect reports from logs
            reports = rec.printed_log_ids.mapped("report_id")

            # Sort for deterministic output
            reports = reports.sorted(lambda report: report.name or "")

            # Remove duplicates preserving order
            unique_names = dict.fromkeys(reports.mapped("display_name"))

            # Join into comma-separated string
            rec.printed_report_names = ", ".join(unique_names)

    def action_view_printed_logs(self):
        """
        Open a tree view displaying printed logs related to this record.

        Returns:
            dict: Standard Odoo action opening ``report.printed.log`` records
                  filtered by this record's (res_model, res_id).

        Notes:
        - Uses ensure_one() as the action is record-specific
        - Designed to be called from UI buttons
        """
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "name": "Printed Logs",
            "res_model": "report.printed.log",
            "view_mode": "tree",
            "domain": [
                ("res_model", "=", self._name),
                ("res_id", "=", self.id),
            ],
        }
