# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo import fields, models
import logging
import json
logger = logging.getLogger(__name__)
try:
    import pandas
    import altair
except ImportError:
    logger.debug('Cannot import altair or pandas')


class KpiKpi(models.Model):

    _inherit = "kpi.kpi"

    widget = fields.Selection(selection_add=[("altair", "Altair")])

    def _get_code_input_dict(self):
        res = super()._get_code_input_dict()
        if self.widget == 'altair':
            res.update({
                'json': json,
                'altair': altair,
                'pandas': pandas,
            })
        return res
