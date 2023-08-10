# Copyright 2020 Creu Blanca
# Copyright 2020 Ecosoft Co., Ltd.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
import json

from werkzeug.urls import url_decode

from odoo.http import request, route

from odoo.addons.web.controllers.report import ReportController


class ReportControllerEncrypt(ReportController):
    @route()
    def report_download(self, data, context=None):
        result = super().report_download(data, context=context)
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
            data = dict(
                url_decode(url.split("?")[1]).items()
            )  # decoding the args represented in JSON
            if "context" in data:
                context, data_context = json.loads(context or "{}"), json.loads(
                    data.pop("context")
                )
                if "encrypt_password" in data_context:
                    encrypted_data = request.env["ir.actions.report"]._encrypt_pdf(
                        result.get_data(), data_context["encrypt_password"]
                    )
                    result.set_data(encrypted_data)
        return result
