# -*- coding: utf-8 -*-

import base64
import json
import lxml.html
import os
import time
import requests
import subprocess
import tempfile
import websocket
from functools import partial
from contextlib import closing

from openerp import api
from openerp import SUPERUSER_ID
from openerp.addons.web.http import request
from openerp.exceptions import AccessError
from openerp.osv import osv
from openerp.sql_db import TestCursor
from openerp.tools import config
from openerp.tools.misc import find_in_path


def _get_chrome_bin():
    # TODO: check for multiple possible names
    return find_in_path('google-chrome-stable')

CHROME_PORT = 9222 # TODO: probably should pick one that's available for sure

CHROME_FLAGS = [
    '--headless',
    '--disable-gpu',
    '--remote-debugging-port={}'.format(CHROME_PORT),

    # from: https://github.com/GoogleChrome/lighthouse/blob/master/chrome-launcher/flags.ts
    # Disable built-in Google Translate service
    '--disable-translate',
    # Disable all chrome extensions entirely
    '--disable-extensions',
    # Disable various background network services, including extension updating,
    #   safe browsing service, upgrade detector, translate, UMA
    '--disable-background-networking',
    # Disable fetching safebrowsing lists, likely redundant due to disable-background-networking
    '--safebrowsing-disable-auto-update',
    # Disable syncing to a Google account
    '--disable-sync',
    # Disable reporting to UMA, but allows for collection
    '--metrics-recording-only',
    # Disable installation of default apps on first run
    '--disable-default-apps',
    # Skip first run wizards
    '--no-first-run',
]

class Report(osv.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name,
                 html=None, data=None, context=None):

        # TODO check report type
        use_wkhtmltopdf = False

        if use_wkhtmltopdf:
            return super(Report, self).get_pdf(
                cr, uid, ids, report_name, html=html,
                data=data, context=context)

        if context is None:
            context = {}

        if not config['test_enable']:
            context['commit_assetsbundle'] = True

        if html is None:
            html = self.get_html(cr, uid, ids, report_name,
                                 data=data, context=context)

        if isinstance(cr, TestCursor):
            return html

        html = html.decode('utf-8')

        report = self._get_report_from_name(cr, uid, report_name)

        save_in_attachment = self._check_attachment_use(cr, uid, ids, report,
                                                        context=context)

        if not report.paperformat_id:
            user = self.pool['res.users'].browse(cr, uid, uid)
            paperformat = user.company_id.paperformat_id
        else:
            paperformat = report.paperformat_id

        contenthtml = []
        irconfig_obj = self.pool['ir.config_parameter']
        base_url = irconfig_obj.get_param(cr, SUPERUSER_ID, 'report.url') or\
            irconfig_obj.get_param(cr, SUPERUSER_ID, 'web.base.url')

        view_obj = self.pool['ir.ui.view']
        render_minimal = partial(view_obj.render, cr, uid,
                                 'report_render_chrome.chrome_minimal_layout', context=context)

        try:
            root = lxml.html.fromstring(html)
            for node in root.xpath(
    "//div[contains(concat(' ', normalize-space(@class), ' '), ' page ')]"
                    ):
                if ids and len(ids) == 1:
                    reportid = ids[0]
                else:
                    oemodelnode = node.find(
                        ".//*[@data-oe-model=%r]" % report.model)
                    if oemodelnode is not None:
                        reportid = oemodelnode.get('data-oe-id')
                        if reportid:
                            reportid = int(reportid)
                    else:
                        reportid = False

                body = lxml.html.tostring(node)
                reportcontent = render_minimal({
                    'subst': False,
                    'body': body,
                    'base_url': base_url
                })

                contenthtml.append((reportid, reportcontent))

        except lxml.etree.XMLSyntaxError:
            contenthtml = [html]
            save_in_attachment = {}

        specific_paperformat_args = {}
        for attribute in root.items():
            if attribute[0].startswith('data-report-'):
                specific_paperformat_args[attribute[0]] = attribute[1]

        return self._run_chrome(cr, uid, contenthtml, context.get('landscape'),
                                paperformat, specific_paperformat_args,
                                save_in_attachment,
                                context.get('set_viewport_size'), context)

    def _run_chrome(self, cr, uid, bodies, landscape, paperformat,
                    spec_paperformat_args=None, save_in_attachment=None,
                    set_viewport_size=False, context=None):
        """Converts html to a pdf document using Chrome.

        :param bodies: list of string containing the reports
        :param landscape: boolean to force the pdf to be rendered under a landscape format
        :param paperformat: ir.actions.report.paperformat to generate the printToPdf arguments
        :param specific_paperformat_args: dict of prioritized paperformat arguments
        :param save_in_attachment: dict of reports to save/load in/from the db
        :returns: Content of the pdf as a string
        """

        if not save_in_attachment:
            save_in_attachment = {}


        # TODO viewport size
        # TODO pass the cookie
        # TODO paperformat
        # TODO orientation

        pdfdocuments = []
        temporary_files = []
        body_files = []

        chrome = None

        try:
            for index, reporthtml in enumerate(bodies):
                pdfreport_fd, pdfreport_path = tempfile.mkstemp(suffix='.pdf', prefix='report.tmp.')
                temporary_files.append(pdfreport_path)

                # Directly load the document if we already have it
                if save_in_attachment and save_in_attachment['loaded_documents'].get(reporthtml[0]):
                    with closing(os.fdopen(pdfreport_fd, 'w')) as pdfreport:
                        pdfreport.write(save_in_attachment['loaded_documents'][reporthtml[0]])
                    pdfdocuments.append(pdfreport_path)
                    continue
                else:
                    os.close(pdfreport_fd)

                # Body stuff
                content_file_fd, content_file_path = tempfile.mkstemp(suffix='.html', prefix='report.body.tmp.')
                temporary_files.append(content_file_path)
                body_files.append(('file://' + content_file_path, pdfreport_path))
                with closing(os.fdopen(content_file_fd, 'w')) as content_file:
                    content_file.write(reporthtml[1])

            # Execute Chrome
            cmd = [_get_chrome_bin()] + CHROME_FLAGS + [h for h,p in body_files]
            chrome = subprocess.Popen(cmd)

            # Find the websocket URL
            c = False
            while not c:
                try:
                    pages = requests.get('http://127.0.0.1:{}/json'.format(CHROME_PORT)).json()
                    c = True
                except requests.exceptions.ConnectionError:
                    # The process might not have fully started yet. Try again
                    # TODO: limit the number of attempts
                    time.sleep(1)

            for i, (_, pdfreport_path) in enumerate(body_files):
                ws_url = pages[i]['webSocketDebuggerUrl']
                socket = websocket.create_connection(ws_url)

                message = {
                    'id': i,
                    'method': 'Page.printToPDF',
                    'params': {
                        'printBackground': False,
                        'landscape': False,
                        'displayHeaderFooter': False,
                        'scale': 1.0,
                        'paperWidth': 8.5,
                        'paperHeight': 11.0,
                        'marginTop': 0.4,
                        'marginBottom': 0.4,
                        'marginLeft': 0.4,
                        'marginRight': 0.4,
                        'pageRanges': '',
                        'ignoreInvalidPageRanges': False
                    }
                }

                socket.send(json.dumps(message))
                response = json.loads(socket.recv())
                if 'result' not in response:
                    print response
                    raise
                data = response['result']['data']  # TODO: check for errors

                with open(pdfreport_path, 'wb') as f:
                    f.write(base64.decodestring(response['result']['data']))

                if reporthtml[0] is not False and save_in_attachment.get(reporthtml[0]):
                    attachment = {
                        'name': save_in_attachment.get(reporthtml[0]),
                        'datas': data,
                        'datas_fname': save_in_attachment.get(reporthtml[0]),
                        'res_model': save_in_attachment.get('model'),
                        'res_id': reporthtml[0],
                    }
                    try:
                        self.pool['ir.attachment'].create(cr, uid, attachment, context)
                    except AccessError:
                        _logger.info("Cannot save PDF report %r as attachment", attachment['name'])
                    else:
                        _logger.info('The PDF document %s is now saved in the database',
                                     attachment['name'])

                pdfdocuments.append(pdfreport_path)

        finally:
            if chrome is not None:
                chrome.terminate()

        # Return the entire document
        if len(pdfdocuments) == 1:
            entire_report_path = pdfdocuments[0]
        else:
            entire_report_path = self._merge_pdf(pdfdocuments)
            temporary_files.append(entire_report_path)

        with open(entire_report_path, 'rb') as pdfdocument:
            content = pdfdocument.read()

        # Manual cleanup of the temporary files
        for temporary_file in temporary_files:
            try:
                os.unlink(temporary_file)
            except (OSError, IOError):
                _logger.error('Error when trying to remove file %s' % temporary_file)

        return content
