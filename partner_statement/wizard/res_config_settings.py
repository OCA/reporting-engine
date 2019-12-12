from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    group_activity_statement = fields.Boolean(
        "Enable OCA Activity Statements",
        group='account.group_account_invoice',
        implied_group='partner_statement.group_activity_statement',
    )

    default_aging_type = fields.Selection(
        [("days", "Age by Days"), ("months", "Age by Months")],
        string="Aging Method",
        required=True,
        default="days",
        default_model="statement.common.wizard",
    )

    default_show_aging_buckets = fields.Boolean(
        string="Show Aging Buckets",
        default_model="statement.common.wizard",
    )

    default_filter_partners_non_due = fields.Boolean(
        string='Exclude partners with no due entries',
        default_model="statement.common.wizard",
    )

    default_filter_negative_balances = fields.Boolean(
        "Exclude Negative Balances",
        default_model="statement.common.wizard",
    )

    group_outstanding_statement = fields.Boolean(
        "Enable OCA Outstanding Statements",
        group='account.group_account_invoice',
        implied_group='partner_statement.group_outstanding_statement',
    )

    def set_values(self):
        self = self.with_context(active_test=False)
        # default values fields
        IrDefault = self.env['ir.default'].sudo()
        for name, field in self._fields.items():
            if (name.startswith("default_") and
                    field.default_model == 'statement.common.wizard'):
                if isinstance(self[name], models.BaseModel):
                    if self._fields[name].type == 'many2one':
                        value = self[name].id
                    else:
                        value = self[name].ids
                else:
                    value = self[name]
                IrDefault.set('activity.statement.wizard', name[8:], value)
                IrDefault.set('outstanding.statement.wizard', name[8:], value)
        return super().set_values()
