# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com/)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import base64
import logging

from odoo import api, models
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)


class Report(models.Model):

    _inherit = 'report'

    @api.model
    def _get_report_from_name(self, report_name):
        """Get the first record of ir.actions.report.xml having the
        ``report_name`` as value for the field report_name.
        """
        res = super(Report, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env['ir.actions.report.xml']
        qwebtypes = ['csv']
        conditions = [('report_type', 'in', qwebtypes),
                      ('report_name', '=', report_name)]
        context = self.env['res.users'].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)

    @api.model
    def get_csv(self, docids, report_name, data=None):
        # Get the ir.actions.report.xml record we are working on.
        report = self._get_report_from_name(report_name)
        # Check if we have to save the report or if we have to get one from the db.
        save_in_attachment = self._check_attachment_use(docids, report)
        res_id = len(docids) == 1 and docids[0]
        if res_id:
            loaded_doc = save_in_attachment['loaded_documents'].get(res_id)
            if loaded_doc:
                return loaded_doc, 'csv'

        data, ext = report.render_csv(docids, data)

        if res_id and data and save_in_attachment.get(res_id):
            attachment = {
                'name': save_in_attachment.get(res_id),
                'datas': base64.encodestring(data),
                'datas_fname': save_in_attachment.get(res_id),
                'res_model': save_in_attachment.get('model'),
                'res_id': res_id,
            }
            try:
                self.env['ir.attachment'].create(attachment)
            except AccessError:
                _logger.info("Cannot save csv report %r as attachment",
                             attachment['name'])
            else:
                _logger.info(
                    'The csv document %s is now saved in the database',
                    attachment['name'])
        return data, ext
