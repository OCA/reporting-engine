# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)

try:
    from bokeh.embed import components
    from bokeh.plotting import figure
    from bokeh.themes import Theme
except ImportError as e:
    _logger.error(e)


class KpiKpi(models.Model):

    _inherit = "kpi.kpi"

    widget = fields.Selection(
        selection_add=[("bokeh", "Bokeh")], ondelete={"bokeh": "cascade"}
    )

    def _get_bokeh_theme(self):
        return Theme(
            json={
                "attrs": {
                    "Figure": {
                        "background_fill_alpha": 0,
                        "border_fill_alpha": 0,
                        "outline_line_alpha": 0,
                    },
                    "Legend": {
                        "border_line_alpha": 0,
                        "background_fill_alpha": 0,
                    },
                    "ColorBar": {
                        "bar_line_alpha": 0,
                        "background_fill_alpha": 0,
                    },
                }
            }
        )

    def _get_code_input_dict(self):
        res = super()._get_code_input_dict()
        if self.widget == "bokeh":
            res.update(
                {
                    "figure": figure,
                    "components": components,
                    "simple_components": lambda r: components(
                        r, theme=self._get_bokeh_theme()
                    ),
                }
            )
        return res
