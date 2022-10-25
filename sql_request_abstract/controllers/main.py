# Part of Odoo. See LICENSE file for full copyright and licensing details.

import werkzeug

from odoo import http
from odoo.http import request
from odoo.tools.misc import file_open

from odoo.addons.web.controllers.webclient import WebClient


class SqlRequestAbstractWebClient(WebClient):

    # if a field, widget="ace" option="{'mode': 'xxx'}"
    # is present, The ace lib (odoo/addons/web/static/lib/ace)
    # will generate a call to /web/static/lib/ace/mode-xxx.js
    # to load the javascript syntax file.
    # We catch this call and redirect on the correct path
    @http.route("/web/static/lib/ace/mode-pgsql.js", type="http", auth="none")
    def call_mode_pgsql_file(self):
        return http.Response(
            werkzeug.wsgi.wrap_file(
                request.httprequest.environ,
                file_open("sql_request_abstract/static/lib/ace/mode-pgsql.js", "rb"),
            ),
            content_type="application/javascript; charset=utf-8",
            headers=[("Cache-Control", f"max-age={http.STATIC_CACHE}")],
            direct_passthrough=True,
        )
