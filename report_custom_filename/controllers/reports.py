# -*- coding: utf-8 -*-
# Copyright 2014 Therp BV (<http://therp.nl>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import json
from openerp import http
from openerp.addons.web.controllers import main
from openerp.addons.mail.models import mail_template


class Reports(main.Reports):
    @http.route('/web/report', type='http', auth="user")
    @main.serialize_exception
    def index(self, action, token):
        result = super(Reports, self).index(action, token)
        action = json.loads(action)
        context = dict(http.request.context)
        context.update(action["context"])
        report_xml = http.request.env['ir.actions.report.xml']
        reports = report_xml.search([
            ('report_name', '=', action['report_name']),
            ('download_filename', '!=', False)])
        for report in reports:
            objects = http.request.session.model(context['active_model'])\
                .browse(context['active_ids'])
            generated_filename = mail_template.mako_template_env\
                .from_string(report.download_filename)\
                .render({
                    'objects': objects,
                    'o': objects[0],
                    'object': objects[0],
                })
            result.headers['Content-Disposition'] = main.content_disposition(
                generated_filename)
        return result
