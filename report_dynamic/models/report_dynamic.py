from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportDynamic(models.Model):
    _name = "report.dynamic"
    _description = "Dynamically create reports"

    name = fields.Char(required=True)
    model_id = fields.Many2one("ir.model")
    # Inform the user about configured model_id
    # in template
    model_name = fields.Char(related="model_id.name")
    model_model = fields.Char(related="model_id.model", string="Tech name of model_id")
    res_id = fields.Integer()
    resource_ref = fields.Reference(
        string="Target record",
        selection="_selection_target_model",
        compute="_compute_resource_ref",
        inverse="_inverse_resource_ref",
        store=True,
    )
    wrapper_report_id = fields.Many2one("ir.ui.view", domain="[('type', '=', 'qweb')]")
    template_id = fields.Many2one(
        "report.dynamic",
        domain="[('is_template', '=', True)]",
        copy=False,
        default=lambda self: self.env.company.external_report_layout_id,
    )
    report_ids = fields.One2many(
        "report.dynamic",
        "template_id",
        domain="[('is_template', '=', False)]",
        copy=False,
    )
    documentation = fields.Text(default="Documentation placeholder", readonly=True)
    condition_domain_global = fields.Char(
        string="Global domain condition", default="[]"
    )
    active = fields.Boolean(default=True)
    is_template = fields.Boolean(default=False)
    lock_date = fields.Date()
    field_ids = fields.Many2many(
        "ir.model.fields", "contextual_field_rel", "contextual_id", "field_id", "Fields"
    )
    window_action_exists = fields.Boolean(compute="_compute_window_action_exists")
    group_by_record_name = fields.Char(
        compute="_compute_group_by_record_name",
        store=True,
        help="Computed field for grouping by record name in search view",
    )

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.depends("model_id", "res_id", "template_id")
    def _compute_resource_ref(self):
        for this in self:
            model = (
                this.model_id.model
                if this.is_template
                else this.template_id.model_id.model
            )
            if model:
                # Return a meaningful message anytime this breaks
                try:
                    sample_record = self.env[model].search([], limit=1)
                except Exception as e:
                    raise UserError(
                        _("Model {} is not applicable for report. Reason: {}").format(
                            model, str(e)
                        )
                    )
                # Tackle the problem of non-existing sample record
                if not sample_record:
                    raise UserError(
                        _(
                            "No sample record exists for Model {}. "
                            "Please create one before proceeding"
                        ).format(model)
                    )
                # we need to give a default to id part of resource_ref
                # otherwise it is not editable
                this.resource_ref = "{},{}".format(
                    model, this.res_id or sample_record.id,
                )
            else:
                this.resource_ref = False

    def _inverse_resource_ref(self):
        for this in self:
            if this.resource_ref:
                this.res_id = this.resource_ref.id
                this.model_id = (
                    self.env["ir.model"]
                    .search([("model", "=", this.resource_ref._name)], limit=1)
                    .id
                )

    def get_window_actions(self):
        return self.env["ir.actions.act_window"].search(
            [
                ("res_model", "=", "wizard.report.dynamic"),
                ("binding_model_id", "=", self.model_id.id),
            ]
        )

    def _compute_window_action_exists(self):
        for this in self:
            this.window_action_exists = bool(this.get_window_actions())

    @api.depends("resource_ref")
    def _compute_group_by_record_name(self):
        for this in self:
            this.group_by_record_name = ""
            if this.is_template:
                continue
            if hasattr(this.resource_ref, "name"):
                this.group_by_record_name = this.resource_ref.name
                continue
            # TODO: this is plainly wrong, fix
            this.group_by_record_name = _("{} - {}").format(
                this.resource_ref._name, this.resource_ref.id
            )

    def get_template_xml_id(self):
        self.ensure_one()
        if not self.wrapper_report_id:
            # return a default
            return "web.external_layout"
        record = self.env["ir.model.data"].search(
            [("model", "=", "ir.ui.view"), ("res_id", "=", self.wrapper_report_id.id)],
            limit=1,
        )
        return "{}.{}".format(record.module, record.name)

    section_ids = fields.One2many("report.dynamic.section", "report_id", copy=True)
    section_count = fields.Integer(string="Sections", compute="_compute_section_count")

    @api.depends("section_ids")
    def _compute_section_count(self):
        for this in self:
            this.section_count = len(this.section_ids)

    def action_view_section(self):
        self.ensure_one()
        return {
            "name": _("Sections"),
            "type": "ir.actions.act_window",
            "res_model": "report.dynamic.section",
            "view_mode": "tree,form",
            "target": "current",
            "context": {"default_report_id": self.id},
            "domain": [("id", "in", self.section_ids.ids)],
        }

    def action_wizard_lock_report(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "wizard.lock.report",
            "view_mode": "form",
            "target": "new",
        }

    def action_preview_content(self):
        self.ensure_one()
        action = self.env.ref("report_dynamic.report_dynamic_document_preview").read(
            []
        )[0]
        return action

    def action_toggle_active(self):
        self.ensure_one()
        self.active = not self.active

    # Override create() and write() to keep
    # resource_ref always the same with template
    # even if template.resource_ref=False
    @api.model
    def create(self, values):
        records = super().create(values)
        for this in records:
            if this.template_id.resource_ref and not this.res_id:
                this.resource_ref = this.template_id.resource_ref
                # Give a default to wrapper_report_id when
                # user sets template_id
                this.wrapper_report_id = this._set_wrapper_report_id(this.template_id)
        return records

    def write(self, values):
        # If the template is changed back to a non-template
        # (eg is_template is set to False),
        # and the template already has children, then disallow.
        if all(
            [
                self.report_ids,
                self.is_template,
                "is_template" in values,
                values.get("is_template") is False,
            ]
        ):
            raise UserError(
                _(
                    "You cannot switch this template because "
                    "it has reports connected to it"
                )
            )
        # If the model is changed while
        # the template already has children, disallow;
        if all(
            [
                self.report_ids,
                "model_id" in values,
                self.model_id != self.env["ir.model"].browse(values.get("model_id")),
            ]
        ):
            raise UserError(_("You cannot change model for this report"))
        if "template_id" in values and values.get("template_id"):
            # if in a report we set a template
            template = self.browse(values.get("template_id"))
            self.resource_ref = template.resource_ref
            # Give a default to wrapper_report_id when
            # user sets template_id
            self.wrapper_report_id = self._set_wrapper_report_id(template)
        return super().write(values)

    def unlink(self):
        for this in self:
            if not this.is_template:
                continue
            if this.window_action_exists:
                this.unlink_action()
        return super().unlink()

    def _set_wrapper_report_id(self, template):
        self.ensure_one()
        return template.wrapper_report_id or self.env.company.external_report_layout_id

    # Contextual action for dynamic reports
    def create_action(self):
        self.ensure_one()
        if self.window_action_exists:
            return
        if not self.model_id:
            return
        self.env["ir.actions.act_window"].create(
            {
                "name": "Dynamic Reporting",
                "type": "ir.actions.act_window",
                "res_model": "wizard.report.dynamic",
                "context": "{'mass_report_object' : %d}" % (self.id),
                "domain": [("model_id", "=", self.model_id.id)],
                "view_mode": "form",
                "target": "new",
                "binding_type": "action",
                "binding_model_id": self.model_id.id,
            }
        )

    def unlink_action(self):
        # We make sudo as any user with rights in this model should be able
        # to delete the action, not only admin
        self.env["ir.actions.act_window"].search(
            [
                ("res_model", "=", "wizard.report.dynamic"),
                ("binding_model_id", "=", self.model_id.id),
            ]
        ).sudo().unlink()
