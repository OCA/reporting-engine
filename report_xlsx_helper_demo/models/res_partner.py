# Copyright 2009-2018 Noviat
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    @api.multi
    def export_xls(self):
        module = __name__.split('addons.')[1].split('.')[0]
        report_name = '{}.partner_export_xlsx'.format(module)
        report = {
            'type': 'ir.actions.report',
            'report_type': 'xlsx',
            'report_name': report_name,
            # model name will be used if no report_file passed via context
            'context': dict(self.env.context, report_file='partner'),
            # report_xlsx doesn't pass the context if the data dict is empty
            # cf. report_xlsx\static\src\js\report\qwebactionmanager.js
            # TODO: create PR on report_xlsx to fix this
            'data': {'dynamic_report': True},
        }
        return report
