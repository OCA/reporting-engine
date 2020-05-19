# Copyright 2020 Ecosoft Co., Ltd (http://ecosoft.co.th)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from suds.client import Client
from xml.etree import ElementTree as ET

 
class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    jasper_url = fields.Char(
        string="Jasper Server URL",
        default="http://localhost:8080/jasperserver/services/repository?wsdl",
    )
    jasper_username = fields.Char(
        string="User Name",
    )
    jasper_password = fields.Char(
        string="Password",
    )
    jasper_report_path = fields.Char(
        string="Jaser Server Report Path",
    )
    parameter_name = fields.Char(
        string="Jasper Parameter Name",
    )    
    criteria_field = fields.Char(
        string="Criteria Field",
    )
    report_type = fields.Selection(
        selection_add=[
            ("jasperserver", "Jasper Server"),
        ]
    )

    def gererate_pdf(self, docids, data):
        url = self.jasper_url
        user = self.jasper_username
        password = self.jasper_password
        report_path = self.jasper_report_path
        format = 'pdf'
        client = Client(url, username=user, password=password)
        client.set_options(retxml=True)
        req = self.createRequest(
           arguments={"RUN_OUTPUT_FORMAT" : format},
           uriString=report_path,
           wsType="reportUnit",
           operationName="runReport",
           params={},
        )
        res = client.service.runReport(req)
        return res

    def createRequest(self, **kwargs):
        r = ET.Element("request")
        r.set("operationName",kwargs.get("operationName", "list"))
        for argName,argValue in kwargs.get("arguments",{}).items():
            ar = ET.SubElement(r,"argument")
            ar.set("name",argName)
            ar.text = argValue
        rd = ET.SubElement(r,"resourceDescriptor")
        rd.set("name","")
        rd.set("wsType",kwargs.get("wsType","folder"))
        rd.set("uriString",kwargs.get("uriString",""))
        l = ET.SubElement(rd,"label")
        l.text = "null"
        for pname,pval in kwargs.get("params",{}).items():
            if type(pval) in (list,tuple):
                for aval in pval:
                    p = ET.SubElement(rd,"parameter")
                    p.set("name",pname)
                    p.set("isListItem","true")
                    p.text = aval
            else:
                p = ET.SubElement(rd,"parameter")
                p.set("name",pname)
                p.text = pval
        return ET.tostring(r, encoding='unicode')

    def render_jasperserver_pdf(self, docids, data):
        return self.gererate_pdf(docids, data), "pdf"

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