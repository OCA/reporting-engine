# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

from io import StringIO

from odoo import models

import logging
_logger = logging.getLogger(__name__)

try:
    import csv
except ImportError:
    _logger.debug('Can not import csvwriter`.')


class ReportCSVAbstract(models.AbstractModel):
    _name = 'report.report_csv.abstract'
    _description = 'Abstract Model for CSV reports'

    def _get_objs_for_report(self, docids, data):
        """
        Returns objects for csv report.  From WebUI these
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
        return self.env[self.env.context.get('active_model')].browse(ids)

    def create_csv_report(self, docids, data):
        objs = self._get_objs_for_report(docids, data)
        file_data = StringIO()
        file = csv.DictWriter(file_data, **self.csv_report_options())
        self.generate_csv_report(file, data, objs)
        file_data.seek(0)
        return file_data.read(), 'csv'

    def csv_report_options(self):
        """
        :return: dictionary of parameters. At least return 'fieldnames', but
        you can optionally return parameters that define the export format.
        Valid parameters include 'delimiter', 'quotechar', 'escapechar',
        'doublequote', 'skipinitialspace', 'lineterminator', 'quoting'.
        """
        return {'fieldnames': []}

    def generate_csv_report(self, file, data, objs):
        raise NotImplementedError()
