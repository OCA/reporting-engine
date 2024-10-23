# Copyright 2024 Akretion
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

import base64

import requests

from odoo import api, fields, models

# Make it depends on model ?
DIR = "erp"


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("libreoffice", "LibreOffice")],
        ondelete={"libreoffice": "set default"},
    )
    output_type = fields.Selection(
        selection=[
            ("odt", "ODT"),
            ("pdf", "PDF"),
            ("html", "HTML"),
            ("docx", "DOCX"),
            ("png", "PNG"),
        ]
    )
    doc_template = fields.Binary(string="LibreOffice template", attachment=False)

    @api.model
    def _render_libreoffice(self, report_ref, docids, data):
        """
➤ curl -X PUT -H 'secret_key: aaa' -H 'directory: test_dir1' http://localhost:8000/         dim. 02 juin 2024 10:24:17
{"directory":"test_dir1","message":"Successfully created"}
dav@nx1:~/dvp/anothercorp|niam⚡*?
➤ curl -X PUT -H 'secret_key: aaa' -F file=@./lot.odt http://localhost:8000/test_dir1       dim. 02 juin 2024 10:26:04
{"file":"lot.odt","message":"Successfully uploaded","variables":{"my_tag":{"type":"text","value":""},"other_tag":{"type":"text","value":""}}}
dav@nx1:~/dvp/anothercorp|niam⚡*?
➤ curl -X POST \\                                                                    492ms  dim. 02 juin 2024 10:27:24
          -H 'secret_key: aaa' \
          -H 'Content-Type: application/json' \
          -d '[{"name":"my_file.odt","variables":{"my_tag":{"type":"text","value":"foo"},"other_tag":{"type":"text","value":"bar"}}}]' \
          --output titi.odt http://localhost:8000/test_dir1/lot.odt
        """
        self.model_id.model
        param_m = self.env["ir.config_parameter"]
        url = "%s:%s" % (
            param_m.get_param("libreoffice_url"),
            param_m.get_param("libreoffice_port"),
        )
        headers = {
            "directory": DIR,
            "secret_key": param_m.get_param("libreoffice_secret"),
        }
        response = requests.put(
            url, headers=headers, data=base64.decodebytes(self.doc_template)
        )
        import pdb

        pdb.set_trace()
        if response.status_code == 200:
            assert (
                response.content
                == b'{"directory":"erp","message":"Successfully created"}\n'
            )
            print("yes")
        # recup file
        # scan file and get keys
        # set/send mapping
        # get replacement
        # get populated file
        # return file

    @api.model
    def render_libreoffice(self, template, data):
        url = "http://localhost:8000/"  # URL du service LO Template
        files = {"file": open(template, "rb")}

        # Envoyer le fichier template au service LO Template
        response = requests.put(url, headers=headers, files=files)
        if response.status_code == 200:
            variables = response.json().get("variables")
            payload = {"template": template, "variables": variables}

            # Demander la génération du document
            response = requests.post(url + "generate", json=payload, headers=headers)
            if response.status_code == 200:
                return response.content
        return None

    @api.model
    def _get_report_from_name(self, report_name):
        res = super(IrActionsReport, self)._get_report_from_name(report_name)
        if res:
            return res
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["libreoffice"]
        conditions = [
            ("report_type", "in", qwebtypes),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        return report_obj.with_context(**context).search(conditions, limit=1)
