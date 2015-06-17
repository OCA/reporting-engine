# -*- encoding: utf-8 -*-

# Odoo, Open Source Management Solution
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from os import path
from openerp import api, models


class XSDSampleReport(models.AbstractModel):
    """This report is checked against an XSD before downloading.

    The XML itself is declared in ``./views/res_partner_templates.xml``, and
    the XSD can be found in ``./xsd/sample_report.xsd``.

    This model's :attr:`._name` must be ``report.<XML ID of template>``.
    """
    _name = "report.report_xml_sample.xsd_sample_report"
    _inherit = "report_xml.xsd_checked_report"

    @api.multi
    def xsd(self):
        """Return the XSD schema contents."""
        file = path.join(path.dirname(__file__), "xsd", "sample_report.xsd")
        with open(file) as xsd:
            return xsd.read()
