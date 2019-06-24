# Copyright 2018 Hugo Rodrigues
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import http, models, api, fields, tools, exceptions, _ 
from werkzeug import urls
import requests
import datetime
import functools
import dateutil.relativedelta as relativedelta
import copy
import time
from odoo.tools.safe_eval import safe_eval

CONTROLLER_TYPES = [("controller", "Controller")]
CONTROLLER_KEYS = [x[0] for x in CONTROLLER_TYPES]

PDF_MAGIC = b"%PDF"

CONTENT_TYPES = [('multipart/form-data', 'Form'),
                 ('application/json', 'JSON')]

class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"
    _sql_constraints = [
        ("check_controller_url",
         "CHECK(report_type NOT ILIKE 'controller%' OR "
         "controller_url IS NOT NULL)",
         _("A controller report must have a URL"))
    ]

    report_type = fields.Selection(selection_add=CONTROLLER_TYPES,
                                   help="The type of the report that will be rendered, each one having its own rendering method. HTML means the report will be opened directly in your browser PDF means the report will be rendered using Wkhtmltopdf and downloaded by the user Controller means the it will be use a controller or url and download the report from another origin.")
    controller_document_type = fields.Char("Document Type", default="pdf")
    
    #Destination Controller Content Type, in case controller wants json request
    controller_content_type = fields.Selection(CONTENT_TYPES, "Content Type", help="Controller request content type.", default='multipart/form-data')

    controller_url = fields.Char("Controller URL", help="Controller from url to fetch. You can use a python expression with the 'object' and 'time' variables.")

    #André Liu - Improvements To Do
    #Controller Data
    #Additional Controller header information
    #Allow different type of controllers

    @api.multi
    def render_controller(self, res_ids, data=None):
        """
        This method gets the PDF report from a URL
        """
        self.ensure_one()
        if not data:
            data = {}
        #Controller report must have document type, default is pdf
        if not self.controller_document_type:
            raise exceptions.ValidationError(_("Controller has no document type!"))

        url = self.controller_url
        
        #Dict for constructing controller URL
        localdict = {
            'time': time
        }
        if isinstance(res_ids, list) and \
                all([isinstance(x, (int, str)) for x in res_ids]):
            docs = self.env[self.model].browse(res_ids)
            localdict['object'] = docs
        else:
            localdict['object'] = self.env[self.model]
            
        #Rendering controller URL
        url = safe_eval(url, localdict)
        
        #Append host if controller does not start with any of the following strings
        add_host = True
        for h in ['http://', 'https://', 'ftp://']:
            if url.startswith(h):
                add_host = False
                break
        if add_host:
            #Append host
            try:
                host_url = http.request.httprequest.host_url
            except:
                host_url = self.sudo().env['ir.config_parameter'].get_param('web.base.url')
            if host_url:
                if not host_url.endswith('/'):
                    host_url += '/'
                while url.startswith('/'):
                    url = url[1:]
                url = host_url + url
                
        #Set Header and content type
        headers = {
            'Content-Type': self.controller_content_type,
        }
        try:
            #Salvage session id cookie, allows for request to be recognized as the same session request
            headers['cookie'] = 'session_id=%s;frontend_lang=%s' % (http.request.httprequest.cookies['session_id'], http.request.httprequest.cookies['frontend_lang'])
        except:
            pass
        try:
            #Added just in case it's lang dependent
            headers['Accept-Language'] = http.request.httprequest.accept_languages.to_header()
        except:
            pass
        
        #Fetch document
        response = requests.get(url, headers=headers)
        
        #Return error if not PDF
        #Perhaps later we may wish to have other document types.
        if response.content[:4] != PDF_MAGIC:
            error_msg = _("Controller result isn't a PDF")
            raise exceptions.ValidationError(error_msg)
        return response.content, self.controller_document_type
