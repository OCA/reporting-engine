# Copyright 2022 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ReportDynamic(models.Model):
    _name = "report.dynamic"
    _description = "Dynamically create reports"

    name = fields.Char(required=True)
    model_id = fields.Many2one(comodel_name="ir.model")
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
    wrapper_report_id = fields.Many2one(
        comodel_name="ir.ui.view", domain="[('type', '=', 'qweb')]"
    )
    template_id = fields.Many2one(
        comodel_name="report.dynamic",
        domain="[('is_template', '=', True)]",
        copy=False,
        default=lambda self: self.env.company.external_report_layout_id,
    )
    report_ids = fields.One2many(
        comodel_name="report.dynamic",
        inverse_name="template_id",
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
        comodel_name="ir.model.fields",
        relation="contextual_field_rel",
        column1="contextual_id",
        column2="field_id",
        string="Fields",
    )
    window_action_exists = fields.Boolean(compute="_compute_window_action_exists")
    group_by_record_name = fields.Char(
        compute="_compute_group_by_record_name",
        store=True,
        help="Computed field for grouping by record name in search view",
    )
    section_ids = fields.One2many(
        comodel_name="report.dynamic.section", inverse_name="report_id", copy=True
    )
    section_count = fields.Integer(string="Sections", compute="_compute_section_count")

    @api.model
    def _selection_target_model(self):
        models = self.env["ir.model"].search([])
        return [(model.model, model.name) for model in models]

    @api.depends("model_id", "res_id", "template_id")
    def _compute_resource_ref(self):
        for rec in self:
            model = (
                rec.model_id.model
                if rec.is_template
                else rec.template_id.model_id.model
            )
            if not model:
                rec.resource_ref = False
                continue
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
            rec.resource_ref = "{},{}".format(model, rec.res_id or sample_record.id,)

    def _inverse_resource_ref(self):
        for rec in self:
            if rec.resource_ref:
                rec.res_id = rec.resource_ref.id
                rec.model_id = self.env["ir.model"]._get(rec.resource_ref._name)

    def get_window_actions(self):
        return self.env["ir.actions.act_window"].search(
            [
                ("res_model", "=", "wizard.report.dynamic"),
                ("binding_model_id", "=", self.model_id.id),
            ]
        )

    def _compute_window_action_exists(self):
        for rec in self:
            rec.window_action_exists = bool(rec.get_window_actions())

    @api.depends("resource_ref")
    def _compute_group_by_record_name(self):
        for rec in self:
            rec.group_by_record_name = ""
            if rec.is_template:
                continue
            if hasattr(rec.resource_ref, "display_name"):
                rec.group_by_record_name = rec.resource_ref.display_name
                continue
            # TODO: this is plainly wrong, fix
            rec.group_by_record_name = _("{} - {}").format(
                rec.resource_ref._name, rec.resource_ref.id
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

    @api.depends("section_ids")
    def _compute_section_count(self):
        for rec in self:
            rec.section_count = len(rec.section_ids)

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
        for rec in records:
            if rec.template_id.resource_ref and not rec.res_id:
                rec.resource_ref = rec.template_id.resource_ref
                # Give a default to wrapper_report_id when
                # user sets template_id
                rec.wrapper_report_id = rec._get_wrapper_report_id(rec.template_id)
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
            self.wrapper_report_id = self._get_wrapper_report_id(template)
        return super().write(values)

    def unlink(self):
        for rec in self:
            if not rec.is_template:
                continue
            if rec.window_action_exists:
                rec.unlink_action()
        return super().unlink()

    def _get_wrapper_report_id(self, template):
        self.ensure_one()
        return template.wrapper_report_id or self.env.company.external_report_layout_id

    # Contextual action for dynamic reports
    def create_action(self):
        self.ensure_one()
        if self.window_action_exists:
            return
        if not self.model_id:
            return
        self.env["ir.actions.act_window"].sudo().create(
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
