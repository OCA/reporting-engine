# Copyright 2022 Sunflower IT <http://sunflowerweb.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval


class ReportDynamic(models.Model):
    _name = "report.dynamic"
    _description = "Dynamically create reports"

    name = fields.Char(required=True)
    real_model_id = fields.Many2one(
        comodel_name="ir.model", domain="[('transient', '=', False)]"
    )
    model_id = fields.Many2one(
        comodel_name="ir.model",
        compute="_compute_model_id",
        inverse="_inverse_model_id",
        store=True,
    )
    # Inform the user about configured model_id
    # in template
    model_model = fields.Char(related="model_id.model", string="Tech name of model_id")
    res_id = fields.Integer(copy=False)
    resource_ref = fields.Reference(
        string="Target record",
        selection="_selection_target_model",
        compute="_compute_resource_ref",
        inverse="_inverse_resource_ref",
    )
    render_resource_ref = fields.Reference(
        selection="_selection_target_model", compute="_compute_render_resource_ref"
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
    is_template = fields.Boolean()
    lock_date = fields.Date(readonly=True)
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
    report_ids = fields.One2many(
        comodel_name="report.dynamic", inverse_name="template_id", copy=False
    )
    report_count = fields.Integer(string="Reports", compute="_compute_report_count")
    section_ids = fields.One2many(
        comodel_name="report.dynamic.section", inverse_name="report_id", copy=True
    )
    section_count = fields.Integer(string="Sections", compute="_compute_section_count")
    preview_res_id = fields.Integer(compute="_compute_preview_res_id")

    _sql_constraints = [
        (
            "template_check",
            """
            CHECK(
                (is_template = 'f' and template_id is not null) or
                (is_template = 't' and template_id is null)
            )
            """,
            "A report should always have a template, but a template cannot have one.",
        ),
        (
            "res_id_check",
            """
            CHECK(
                (is_template = 'f' and res_id is not null) or
                (is_template = 't' and res_id is null)
            )
            """,
            "A report should always relate to a record, but a template cannot have one.",
        ),
    ]

    @api.depends("is_template", "template_id.model_id", "real_model_id")
    def _compute_model_id(self):
        for rec in self:
            if rec.is_template:
                rec.model_id = rec.real_model_id
            else:
                rec.model_id = rec.template_id.model_id

    def _inverse_model_id(self):
        for rec in self:
            if rec.is_template:
                rec.real_model_id = rec.model_id

    @api.depends("resource_ref", "is_template", "preview_res_id")
    def _compute_render_resource_ref(self):
        for rec in self:
            if rec.is_template and rec.preview_res_id and rec.model_id:
                rec.render_resource_ref = "%s,%s" % (
                    rec.model_id.model,
                    rec.preview_res_id,
                )
            elif not rec.is_template:
                rec.render_resource_ref = rec.resource_ref
            else:
                rec.render_resource_ref = False

    @api.model
    def _selection_target_model(self):
        """ These models can be a target for a dynamic report template """
        models = self.env["ir.model"].search([("transient", "=", False)])
        return [(model.model, model.name) for model in models]

    @api.model
    def _get_sample_record(self, model):
        """ Returns any record of given model """
        return self.env[model].search([], limit=1)

    @api.constrains("model_id", "res_id", "template_id")
    def _prevent_broken_models(self):
        """ Prevents user from selecting broken models """
        for rec in self:
            model = rec.model_id.model
            if not model:
                continue
            try:
                self._get_sample_record(model)
            except Exception as e:
                raise ValidationError(
                    _("Model %s is not applicable for report. Reason: %s")
                    % (model, str(e))
                )

    @api.onchange("template_id")
    def _onchange_template_id(self):
        """ When template is chosen, define section_ids """
        for report in self:
            if not report.is_template and report.template_id and not report.section_ids:
                report.section_ids = report.template_id.section_ids

    @api.onchange("model_id")
    def _onchange_model_id(self):
        self.ensure_one()
        res = {}
        model = self.model_id.model
        if not model:
            return res
        try:
            self.env[model].search_read([], limit=1)
        except Exception as e:
            res["warning"] = {
                "message": _("Model %s is not applicable for report. Reason: %s")
                % (model, str(e))
            }
            self.model_id = self._origin.model_id.id
        return res

    @api.depends("model_id", "res_id", "template_id")
    def _compute_resource_ref(self):
        for rec in self:
            if rec.is_template or not rec.model_id:
                rec.resource_ref = False
                continue
            sample_record = self._get_sample_record(rec.model_id.model)
            rec.resource_ref = "%s,%s" % (
                rec.model_id.model,
                rec.res_id or sample_record.id,
            )

    def _inverse_resource_ref(self):
        for rec in self:
            if rec.resource_ref:
                rec.res_id = rec.resource_ref.id
                rec.model_id = self.env["ir.model"]._get(rec.resource_ref._name)
            else:
                rec.res_id = None

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
            if rec.is_template or not rec.resource_ref:
                continue
            rec.group_by_record_name = rec.resource_ref.display_name

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

    def action_view_sections(self):
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

    @api.depends("report_ids")
    def _compute_report_count(self):
        for rec in self:
            rec.report_count = len(rec.report_ids)

    def action_view_reports(self):
        self.ensure_one()
        return {
            "name": _("Reports"),
            "type": "ir.actions.act_window",
            "res_model": "report.dynamic",
            "view_mode": "tree,form",
            "target": "current",
            "context": {
                "default_is_template": False,
                "is_template": False,
                "default_template_id": self.id,
            },
            "domain": [("id", "in", self.report_ids.ids)],
        }

    def action_wizard_lock_report(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "wizard.lock.report",
            "view_mode": "form",
            "target": "new",
        }

    def _compute_preview_res_id(self):
        for tpl in self:
            domain = safe_eval(tpl.condition_domain_global or "[]")
            record = self.env[self.model_id.model].search(domain)[:1]
            tpl.preview_res_id = record.id

    def action_preview_content(self):
        self.ensure_one()
        if not self.is_template:
            raise ValidationError(_("Can only use preview for templates"))
        if not self.preview_res_id:
            raise ValidationError(
                _("Looking for a random record matching the domain, but did not find")
            )
        action = self.env.ref("report_dynamic.report_dynamic_document_preview").read(
            []
        )[0]
        return action

    def action_quick_view_content(self):
        self.ensure_one()
        if self.is_template:
            raise ValidationError(_("Can only use quick view for reports"))
        if not self.resource_ref:
            raise ValidationError(_("Needs a record for previewing"))
        action = self.env.ref("report_dynamic.report_dynamic_document_preview").read(
            []
        )[0]
        return action

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

    def action_duplicate_as_template(self):
        self.ensure_one()
        if self.is_template:
            raise ValidationError(
                _("This is not a report, you cannot create a template from it")
            )
        action = self.env.ref("report_dynamic.report_dynamic_template_action").read()[0]
        action["context"] = dict(self.env.context)
        action["context"]["form_view_initial_mode"] = "edit"
        action["views"] = [
            (self.env.ref("report_dynamic.report_dynamic_form").id, "form")
        ]
        action["res_id"] = self.copy(
            {
                "model_id": self.model_id.id,
                "is_template": True,
                "template_id": False,
                "lock_date": False,
                "resource_ref": False,
                "name": _("New template based on report: %s") % (self.name,),
            }
        ).id
        return action

    @api.constrains("report_ids", "is_template")
    def _constrain_template_status(self):
        """ Disallow revoking template status of a template with children """
        if any(rec.report_ids and not rec.is_template for rec in self):
            raise ValidationError(
                _(
                    "You cannot switch this template because "
                    "it has reports connected to it"
                )
            )

    def _forbid_model_change(self, values):
        """ Disallow changing model of a template with children """
        if "model_id" in values and self.mapped("report_ids"):
            raise ValidationError(
                _(
                    "You cannot change model for this template because "
                    "it has reports connected to it"
                )
            )

    def write(self, values):
        self._forbid_model_change(values)
        ret = super().write(values)
        # Set default wrapper_report and resource_ref when user sets template_id
        if values.get("template_id"):
            for rec in self:
                rec.resource_ref = rec.template_id.resource_ref
                rec.wrapper_report_id = rec._get_wrapper_report_id(rec.template_id)
        return ret

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
        """ Anyone can delete this action """
        # to delete the action, not only admin
        recs = (
            self.env["ir.actions.act_window"]
            .sudo()
            .search(
                [
                    ("res_model", "=", "wizard.report.dynamic"),
                    ("binding_model_id", "=", self.model_id.id),
                ]
            )
        )
        if recs:
            recs.unlink()
