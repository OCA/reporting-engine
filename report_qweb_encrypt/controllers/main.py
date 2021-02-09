# Copyright 2020 Creu Blanca
# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from werkzeug.urls import url_decode

from odoo.http import request, route

from odoo.addons.web.controllers import main as report


class ReportController(report.ReportController):
    @route()
    def report_download(self, data, token):
        result = super().report_download(data, token)
        # When report is downloaded from print action, this function is called,
        # but this function cannot pass context (manually entered password) to
        # report.render_qweb_pdf(), encrypton for manual password is done here.
        requestcontent = json.loads(data)
        url, ttype = requestcontent[0], requestcontent[1]
        if (
            ttype in ["qweb-pdf"]
            and result.headers["Content-Type"] == "application/pdf"
            and "?" in url
        ):
            url_data = dict(url_decode(url.split("?")[1]).items())
            if "context" in url_data:
                context = json.loads(url_data["context"])
                if "encrypt_password" in context:
                    Report = request.env["ir.actions.report"]
                    data = result.get_data()
                    encrypted_data = Report._encrypt_pdf(
                        data, context["encrypt_password"]
                    )
                    result.set_data(encrypted_data)
        return result
