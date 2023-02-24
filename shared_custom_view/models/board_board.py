# Copyright 2023 Camptocamp
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo import api, models


class Board(models.AbstractModel):
    _inherit = "board.board"

    @api.model
    def fields_view_get(
        self, view_id=None, view_type="form", toolbar=False, submenu=False
    ):
        """
        Overrides orm field_view_get.
        @return: Dictionary of Fields, arch and toolbar.
        """

        res = super(Board, self).fields_view_get(
            view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu
        )

        custom_view = self.env["ir.ui.view.custom"].search(
            [("user_id", "=", self.env.uid), ("ref_id", "=", view_id)], limit=1
        )
        if not custom_view:
            shared_custom_view = self.env["ir.ui.view.custom"].search(
                [("user_id", "=", False), ("ref_id", "=", view_id)], limit=1
            )
            if shared_custom_view:
                res.update(
                    {
                        "custom_view_id": shared_custom_view.id,
                        "arch": self._arch_preprocessing(shared_custom_view.arch),
                    }
                )
        return res
