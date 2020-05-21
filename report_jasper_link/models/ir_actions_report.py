# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from suds.client import Client
from xml.etree import ElementTree as ET
import email, re

 
class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    jasper_server_config_id = fields.Many2one(
        comodel_name="jasper.server.config",
        string="Connector",
        ondelete="restrict",
    )
    jasper_report_path = fields.Char(
        string="Report Path",
    )
    jasper_parameter_name = fields.Char(
        string="Report Parameter IDS",
    )
    jasper_parameter_ids = fields.One2many(
        comodel_name="jasper.parameter",
        inverse_name="report_id",
        string="Report Parameter",
    )
    report_type = fields.Selection(
        selection_add=[
            ("jasperserver", "Jasper Server"),
        ]
    )

    @api.onchange("report_type")
    def _onchange_report_type(self):
        self.jasper_server_config_id = False
        self.jasper_report_path = False
        self.jasper_parameter_ids = False

    def create_request(self, **kwargs):
        r = ET.Element("request")
        r.set("operationName", kwargs.get("operationName", "list"))
        for name, value in kwargs.get("arguments", {}).items():
            ar = ET.SubElement(r, "argument")
            ar.set("name", name)
            ar.text = value
        rd = ET.SubElement(r, "resourceDescriptor")
        rd.set("name", "")
        rd.set("wsType", kwargs.get("wsType", "folder"))
        rd.set("uriString", kwargs.get("uriString", ""))
        l = ET.SubElement(rd, "label")
        l.text = "null"
        for pname, pval in kwargs.get("params", {}).items():
            if type(pval) in (list, tuple):
                for aval in pval:
                    p = ET.SubElement(rd, "parameter")
                    p.set("name", pname)
                    p.set("isListItem", "true")
                    p.text = aval
            else:
                p = ET.SubElement(rd, "parameter")
                p.set("name", pname)
                p.text = pval
        return ET.tostring(r).decode()

    def generate_pdf(self, docids):
        client = self.jasper_server_config_id.connect_jasperserver()
        report_param = {}
        if self.jasper_parameter_name:
            report_param[self.jasper_parameter_name] = 'id in %s' % str(tuple(docids)).replace(",)", ")")
        for param in self.jasper_parameter_ids:
            report_param[param["name"]] = param["value"]
        req = self.create_request(
            arguments={"RUN_OUTPUT_FORMAT": "pdf"},
            uriString=self.jasper_report_path,
            wsType = "reportUnit",
            operationName="runReport",
            params=report_param,
        )
        res = client.service.runReport(req).decode("latin-1")
        boundary = re.search(r'----=[^\r\n]*', res).group()
        res = " \n" + res
        res = "Content-Type: multipart/alternative; boundary=%s\n%s" % (boundary, res)
        message = email.message_from_string(res)
        attachment = message.get_payload()[1]
        pdf = attachment.get_payload().encode("latin-1")
        return pdf

    def render_jasperserver_pdf(self, docids, data):
        return self.generate_pdf(docids), "pdf"

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(IrActionsReport, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        reporttypes = ["jasperserver"]
        conditions = [
            ("report_type", "in", reporttypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(context).search(conditions, limit=1)