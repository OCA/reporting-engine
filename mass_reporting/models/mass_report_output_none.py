# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging

from openerp import api, models

_logger = logging.getLogger(__name__)


class MassReportOutputNone(models.AbstractModel):
    _inherit = 'mass.report.output'
    _name = 'mass.report.output.none'
    _description = "None"

    @api.model
    def get_report_types(self):
        return []

    @api.model
    def process_mass_report(self, mass_report_id):
        return True
