# -*- coding: utf-8 -*-
# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import werkzeug
from odoo import http
from odoo.http import request


class Home(http.Controller):

    @http.route('/report/qr', type='http', auth="public")
    def report_qr(self, value, box_size=3, border=3, factory='png', **kwargs):
        try:
            barcode = request.env['report'].qr_generate(
                value, box_size=box_size, border=border,
                factory=factory, **kwargs)
        except (ValueError, AttributeError):
            raise werkzeug.exceptions.HTTPException(
                description='Cannot convert into barcode.')
        if factory != 'png':
            return request.make_response(
                barcode, headers=[('Content-Type', 'image/svg+xml')])
        return request.make_response(
            barcode, headers=[('Content-Type', 'image/png')])
