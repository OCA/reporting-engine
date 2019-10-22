# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import BytesIO

from odoo import models

import logging
_logger = logging.getLogger(__name__)

try:
    import xlsxwriter
except ImportError:
    _logger.debug('Can not import xlsxwriter`.')


class ReportXlsxAbstract(models.AbstractModel):
    _name = 'report.report_xlsx.abstract'

    def _get_objs_for_report(self, docids, data):
        """
        Returns objects for xlx report.  From WebUI these
        are either as docids taken from context.active_ids or
        in the case of wizard are in data.  Manual calls may rely
        on regular context, setting docids, or setting data.

        :param docids: list of integers, typically provided by
            qwebactionmanager for regular Models.
        :param data: dictionary of data, if present typically provided
            by qwebactionmanager for TransientModels.
        :param ids: list of integers, provided by overrides.
        :return: recordset of active model for ids.
        """
        if docids:
            ids = docids
        elif data and 'context' in data:
            ids = data["context"].get('active_ids', [])
        else:
            ids = self.env.context.get('active_ids', [])
        # propagate context anyway
        # let it fail explicitely if `active_model` is not there
        return self.env[self.env.context['active_model']].browse(ids)

    def create_workbook(self, file_data, data, objs, report):
        workbook = xlsxwriter.Workbook(file_data, self.get_workbook_options())
        self.generate_xlsx_report(workbook, data, objs)
        for sheet in workbook.worksheets():
            if report and report.header_id and report.header_id.value:
                sheet.set_header(report.header_id.value,
                                 report.header_id.get_options())
            if report and report.footer_id and report.footer_id.value:
                sheet.set_footer(report.footer_id.value,
                                 report.footer_id.get_options())
        return workbook

    def create_xlsx_report(self, docids, data, report):
        objs = self._get_objs_for_report(docids, data)
        file_data = BytesIO()
        workbook = self.create_workbook(file_data, data, objs, report)
        workbook.close()
        file_data.seek(0)
        return file_data.read(), 'xlsx'

    def get_workbook_options(self):
        """
        See https://xlsxwriter.readthedocs.io/workbook.html constructor options
        :return: A dictionary of options
        """
        return {}

    def generate_xlsx_report(self, workbook, data, objs):
        raise NotImplementedError()

