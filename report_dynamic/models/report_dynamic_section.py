import copy
import traceback

from odoo import _, api, fields, models, tools
from odoo.exceptions import UserError
from odoo.tools import safe_eval

from .header import Header

try:
    from jinja2.sandbox import SandboxedEnvironment

    mako_template_env = SandboxedEnvironment(
        block_start_string="<%",
        block_end_string="%>",
        variable_start_string="${",
        variable_end_string="}",
        comment_start_string="<%doc>",
        comment_end_string="</%doc>",
        line_statement_prefix="%",
        line_comment_prefix="##",
        trim_blocks=True,  # do not output newline after blocks
        autoescape=True,  # XML/HTML automatic escaping
    )
    # Let's keep these in case they are needed
    # in the future
    mako_template_env.globals.update(
        {
            "str": str,
            "len": len,
            "abs": abs,
            "min": min,
            "max": max,
            "sum": sum,
            "filter": filter,
            "map": map,
            "round": round,
            "page": "<p style='page-break-after:always;'/>",
        }
    )
    mako_safe_template_env = copy.copy(mako_template_env)
    mako_safe_template_env.autoescape = False
except ImportError:
    pass


class ReportDynamicSection(models.Model):
    _name = "report.dynamic.section"
    _description = "Section blocks for report.dynamic"

    _order = "sequence"

    name = fields.Char()
    sequence = fields.Integer("Sequence", default=10)
    content = fields.Html("Content")
    dynamic_content = fields.Html(
        compute="_compute_dynamic_content", string="Dynamic Content",
    )
    report_id = fields.Many2one("report.dynamic", string="Report", ondelete="cascade")
    resource_ref = fields.Reference(related="report_id.resource_ref")
    # duplicate the field to avoid including the same field twice in the view
    resource_ref_preview = fields.Reference(
        related="report_id.resource_ref", string="Preview Record", readonly=True
    )
    res_id = fields.Integer(related="report_id.res_id")
    resource_ref_model_id = fields.Many2one("ir.model", related="report_id.model_id")

    # Dynamic field editor
    field_id = fields.Many2one("ir.model.fields", string="Field")
    sub_object_id = fields.Many2one("ir.model", string="Sub-model")
    sub_model_object_field_id = fields.Many2one("ir.model.fields", string="Sub-field")
    default_value = fields.Char("Default Value")
    copyvalue = fields.Char("Placeholder Expression")
    is_paragraph = fields.Boolean(
        default=True, string="Paragraph", help="To highlight lines"
    )
    condition_python = fields.Text(
        string="Python Condition", help="Condition for rendering section",
    )
    condition_domain = fields.Char(string="Domain Condition", default="[]")
    condition_python_preview = fields.Char(
        "Preview", compute="_compute_condition_python_preview"
    )
    model_id_model = fields.Char(
        string="Model _description", related="report_id.model_id.model"
    )

    @api.onchange("field_id", "sub_model_object_field_id", "default_value")
    def onchange_copyvalue(self):
        self.sub_object_id = False
        self.copyvalue = False
        if self.field_id and not self.field_id.relation:
            self.copyvalue = "${{object.{} or {}}}".format(
                self.field_id.name, self._get_proper_default_value()
            )
            self.sub_model_object_field_id = False
        if self.field_id and self.field_id.relation:
            self.sub_object_id = self.env["ir.model"].search(
                [("model", "=", self.field_id.relation)]
            )[0]
        if self.sub_model_object_field_id:
            self.copyvalue = "${{object.{}.{} or {}}}".format(
                self.field_id.name,
                self.sub_model_object_field_id.name,
                self._get_proper_default_value(),
            )

    # this then needs to be an onchange, since user
    # should be able to see preview after setting
    # a condition, directly.
    @api.onchange("condition_python")
    def _compute_condition_python_preview(self):
        """Compute condition and preview"""
        for this in self:
            this.condition_python_preview = False
            if not (this.resource_ref_model_id and this.res_id and this.resource_ref):
                continue
            try:
                # Check if there are any syntax errors etc
                this.condition_python_preview = this._eval_condition_python()
            except Exception as e:
                # and show debug info
                this.condition_python_preview = str(e)
                continue

    def _eval_condition_python(self):
        if not self.condition_python:
            return True
        condition_python = (self.condition_python or "").strip()
        record = self.resource_ref
        if not record:
            return False
        return safe_eval(condition_python, {"object": record})

    def _eval_condition_domain(self):
        condition_domain = (self.condition_domain or "[]").strip()
        return self.resource_ref.filtered_domain(safe_eval(condition_domain))

    def _get_proper_default_value(self):
        self.ensure_one()
        is_num = self.field_id.ttype in ("integer", "float")
        value = 0 if is_num else "''"
        if self.default_value:
            if is_num:
                value = "{}"
            else:
                value = "'{}'"
            value = value.format(self.default_value)
        return value

    # compute the dynamic content for jinja expression
    def _compute_dynamic_content(self):
        # a parent with two children
        h = self._get_header_object()
        for this in self:
            if not (this._eval_condition_python() and this._eval_condition_domain()):
                this.dynamic_content = ""
                continue
            prerendered_content = this._prerender()
            try:
                content = this._render_template(
                    prerendered_content,
                    this.resource_ref_model_id.model,
                    this.res_id,
                    datas={"h": h},
                )
            except Exception:
                this.dynamic_content = "<pre>%s</pre>" % (traceback.format_exc())
            this.dynamic_content = content

    def _get_header_object(self):
        h = Header(child=Header(child=Header()))
        return h

    def _prerender(self):
        """Substitute expressions using report.dynamic.alias records"""
        self.ensure_one()
        content = self.content
        for alias in self.env["report.dynamic.alias"].search(
            [("is_active", "=", True)]
        ):
            if alias.expression_from not in content:
                continue
            content = content.replace(alias.expression_from, alias.expression_to)
        return content

    @api.model
    def _render_template(self, template_txt, model, res_ids, datas=False):
        """
        Render input provided by user, for report and preview
        It is an edited version of mail.template._render_template()
        """
        if isinstance(res_ids, int):
            res_ids = [res_ids]
        if datas and not isinstance(datas, dict):
            raise UserError(_("datas argument is not a proper dict"))
        results = dict.fromkeys(res_ids, u"")
        # try to load the template
        mako_env = mako_safe_template_env
        template = mako_env.from_string(tools.ustr(template_txt))
        records = self.env[model].browse(
            it for it in res_ids if it
        )  # filter to avoid browsing [None]
        res_to_rec = dict.fromkeys(res_ids, None)
        for record in records:
            res_to_rec[record.id] = record
        # prepare template variables
        variables = {
            "ctx": self._context,  # context kw would clash with mako internals
        }
        if datas:
            variables.update(datas)
        for res_id, record in res_to_rec.items():
            variables["object"] = record
            try:
                render_result = template.render(variables)
            except Exception:
                render_result = (
                    "<pre>Section {} could not be rendered {}</pre>"
                ).format(self.name or "(no name set)", traceback.format_exc())
            if render_result == u"False":
                render_result = u""
            results[res_id] = render_result
        return results[res_ids[0]] or results
