# -*- encoding: utf-8 -*-
# Copyright (C) 2014-2015  Grupo ESOC <www.grupoesoc.es>

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
