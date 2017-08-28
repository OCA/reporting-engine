# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import json
import logging
import requests
import subprocess
import time
try:
    import websocket
except ImportError:
    logging.info('Could not load websocket')


from openerp import api, models
from openerp.http import root, request
from openerp.exceptions import UserError
from openerp.sql_db import TestCursor
from openerp.tools import config
from openerp.tools.misc import find_in_path


def _get_chrome_bin():
    result = False
    for binary in ['chrome', 'chromium', 'google-chrome-stable']:
        try:
            result = find_in_path(binary)
        except IOError:
            pass
        if result:
            break
    return result


CHROME_PORT = 9222  # TODO: probably should pick one that's available for sure


CHROME_FLAGS = [
    '--headless',
    '--disable-gpu',
    '--remote-debugging-port={}'.format(CHROME_PORT),

    # from: https://github.com/GoogleChrome/lighthouse/blob/master/
    # chrome-launcher/flags.ts
    # Disable built-in Google Translate service
    '--disable-translate',
    # Disable all chrome extensions entirely
    '--disable-extensions',
    # Disable various background network services, including extension
    # updating, safe browsing service, upgrade detector, translate, UMA
    '--disable-background-networking',
    # Disable syncing to a Google account
    '--disable-sync',
    # Disable reporting to UMA, but allows for collection
    '--metrics-recording-only',
    # Disable installation of default apps on first run
    '--disable-default-apps',
    # Skip first run wizards
    '--no-first-run',
]


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(
        self, cr, uid, ids, report_name, html=None, data=None,
        context=None,
    ):
        # pylint: disable=old-api7-method-defined

        report = self._get_report_from_name(cr, uid, report_name)

        if not report.is_chrome_pdf:
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

        save_in_attachment = self._check_attachment_use(cr, uid, ids, report,
                                                        context=context)

        if not report.paperformat_id:
            user = self.pool['res.users'].browse(cr, uid, uid)
            paperformat = user.company_id.paperformat_id
        else:
            paperformat = report.paperformat_id

        specific_paperformat_args = {}

        return self._run_chrome(
            cr, uid, html, context.get('landscape'),
            paperformat, specific_paperformat_args,
            save_in_attachment,
            context.get('set_viewport_size'), context=context
        )

    @api.v8
    def get_pdf(self, records, report_name, html=None, data=None):
        return self._model.get_pdf(
            self.env.cr, self.env.uid, records.ids, report_name,
            html=html, data=data,
        )

    @api.model
    def _run_chrome(self, html, landscape, paperformat,
                    spec_paperformat_args=None, save_in_attachment=None,
                    set_viewport_size=False):
        if not save_in_attachment:
            save_in_attachment = {}

        # TODO viewport size
        # TODO use fd instead of port

        chrome = None
        content = False

        try:
            # Execute Chrome
            cmd = [_get_chrome_bin()] + CHROME_FLAGS
            chrome = subprocess.Popen(cmd)

            # Find the websocket URL
            pages = False
            while not pages:
                try:
                    pages = requests.get(
                        'http://127.0.0.1:{}/json'.format(CHROME_PORT)
                    ).json()
                except requests.exceptions.ConnectionError:
                    # The process might not have fully started yet. Try again
                    # TODO: limit the number of attempts
                    time.sleep(1)

            for page in pages:
                ws_url = page['webSocketDebuggerUrl']
                socket = websocket.create_connection(ws_url)
                message_id = 1

                def send_message(
                        method, params=None, message_id=message_id,
                        result_key=None
                ):
                    message = {
                        'id': message_id,
                        'method': method,
                        'params': params or {},
                    }
                    socket.send(json.dumps(message))
                    response = json.loads(socket.recv())
                    message_id += 1

                    if 'result' not in response:
                        message = response.get('error', {}).get(
                            'message', str(response)
                        )
                        logging.error(message)
                        raise UserError(message)
                    # TODO: check for errors
                    return response['result'].get(result_key or 'data')

                base_url = self.env['ir.config_parameter'].get_param(
                    'report.url', self.env['ir.config_parameter'].get_param(
                        'web.base.url',
                    )
                )
                send_message('Network.setCookie', {
                    'name': 'session_id',
                    # in a test scenario, there's no request, so we pass some
                    # session_id, as we only need a valid user anyways
                    'value': request and request.session.sid or
                    root.session_store.list()[0],
                    'url': base_url,
                })
                frames = send_message(
                    'Page.getResourceTree', result_key='frameTree'
                )
                send_message('Page.setDocumentContent', {
                    'frameId': frames['frame']['id'],
                    'html': html
                })
                # TODO: here we can get timing issues. Check out what the
                # smartest way is to wait for DocumentReady via DevTools
                content = send_message(
                    'Page.printToPDF', {
                        'landscape': bool(landscape),
                        'displayHeaderFooter': False,
                        'printBackground': True,
                        'scale': 1.0,
                        'paperWidth': paperformat.page_width or 8.5,
                        'paperHeight': paperformat.page_height or 11,
                        'marginTop': '%smm' % (paperformat.margin_top or 0),
                        'marginBottom':
                        '%smm' % (paperformat.margin_bottom or 0),
                        'marginLeft': '%smm' % (paperformat.margin_left or 0),
                        'marginRight':
                        '%smm' % (paperformat.margin_right or 0),
                    }
                )
                content = base64.b64decode(content)
        finally:
            if chrome is not None:
                chrome.terminate()

        return content
