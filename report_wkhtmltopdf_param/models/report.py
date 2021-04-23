# Copyright 2017 Avoin.Systems
# Copyright 2017 Eficent Business and IT Consulting Services, S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        # noinspection PyUnresolvedReferences,PyProtectedMember
        command_args = super(IrActionsReport, self)._build_wkhtmltopdf_args(
            paperformat_id, landscape, specific_paperformat_args, set_viewport_size
        )

        for param in paperformat_id.custom_params:
            try:
                value_index = command_args.index(param.name)
                if param.value:
                    command_args[value_index + 1] = param.value
                else:
                    pass  # param.name is already in command_args
                continue
            except ValueError:
                pass  # param.name is not in command_args
            command_args.extend([param.name])
            if param.value:
                command_args.extend([param.value])

        return command_args
