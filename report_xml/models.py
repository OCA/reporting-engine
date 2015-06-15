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

import logging
from lxml import etree
from openerp import api, fields, models


_logger = logging.getLogger(__name__)


class ReportAction(models.Model):
    _inherit = "ir.actions.report.xml"

    report_type = fields.Selection(selection_add=[("qweb-xml", "XML")])

    def _lookup_report(self, cr, name):
        """Enable ``qweb-xml`` report lookup."""
        try:
            super(ReportAction, self)._lookup_report(cr, name)
        except Exception as ex:
            # Somebody thought it was a good idea to use standard exceptions
            if "qweb-xml" not in ex.message:
                raise ex
            else:
                cr.execute(
                    "SELECT * FROM ir_act_report_xml WHERE report_name=%s",
                    (name,))
                return cr.dictfetchone()["report_name"]

    @api.model
    def render_report(self, res_ids, name, data):
        """Special handling for ``qweb-xml`` reports."""
        if data.get("report_type") == u"qweb-xml":
            new_report = self._lookup_report(name)
            recs = self.env[self.env.context["active_model"]].browse(res_ids)
            result = self.env["report"].get_html(recs, new_report, data=data)

            # XML with spaces before the <?xml tag will fail, and trailing ones
            # do nothing, so let's strip them and make everyone happier
            result = (result.strip(), "xml")
        else:
            result = super(ReportAction, self).render_report(
                res_ids, name, data)

        return result


class ReportGenerator(models.Model):
    _inherit = "report"

    @api.model
    def _get_report_from_name(self, report_name):
        """Allow to view ``qweb-xml`` reports as web pages."""
        try:
            super(ReportGenerator, self)._get_report_from_name(report_name)
        except IndexError:
            return self.env["ir.actions.report.xml"].search(
                [("report_type", "=", "qweb-xml"),
                 ("report_name", "=", report_name)])[0]


class XSDCheckedReport(models.AbstractModel):
    """Check XML report against a XSD schema before downloading it.

    This is an Abstract Model to be inherited by the real report models, which
    must implement :meth:`.xsd` and have a ``_name`` in the form
    ``report.<module>.<report_name>``.
    """
    _name = "report_xml.xsd_checked_report"
    _description = "Base model for reports that need XSD checking"

    @api.multi
    def xsd(self):
        """Return the XSD schema contents."""
        raise NotImplementedError

    @api.multi
    def render_html(self, data=None):
        """Return the XML report after checking it against an XSD.

        If ``context`` contains a dict called ``docargs``, it will be used as
        the Qweb context. The special key ``docs`` will be added to ``docargs``
        automatically if missing.
        """
        # Qweb context
        docargs = self.env.context.get("docargs", dict())
        if "docs" not in docargs:
            docargs["docs"] = (self.env[self.env.context["active_model"]]
                               .browse(self.env.context["active_ids"]))

        # Load XSD
        xsd = etree.XML(self.xsd())
        _logger.debug("XSD schema contents: %s", etree.tostring(xsd))
        xsd = etree.XMLSchema(xsd)
        parser = etree.XMLParser(schema=xsd)

        # Generate XML report
        result = (self.env["report"]
                  .render(self._name[len("report."):], docargs)
                  .strip())

        # Validate XML with XSD
        try:
            etree.fromstring(result, parser)
        except Exception as error:
            _logger.error(result)
            raise error

        return result
