# -*- coding: utf-8 -*-
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64
import logging
import psutil
import subprocess
import threading
import time
try:
    from cproto import CProto
except ImportError:
    logging.info('Could not load cproto')


from openerp import api, models
from openerp.http import root, request
from openerp.tools.misc import find_in_path


LOCALHOST = '127.0.0.1'
_logger = logging.getLogger('report_qweb_chrome_renderer')


class Report(models.Model):
    _inherit = 'report'

    @api.v7
    def get_pdf(
        self, cr, uid, ids, report_name, html=None, data=None,
        context=None,
    ):
        # pylint: disable=old-api7-method-defined
        if context is None:
            context = {}

        report = self._get_report_from_name(cr, uid, report_name)

        if not report.is_chrome_pdf:
            return super(Report, self).get_pdf(
                cr, uid, ids, report_name, html=html,
                data=data, context=context)

        save_in_attachment = self._check_attachment_use(cr, uid, ids, report,
                                                        context=context)

        if not report.paperformat_id:
            user = self.pool['res.users'].browse(cr, uid, uid)
            paperformat = user.company_id.paperformat_id
        else:
            paperformat = report.paperformat_id

        specific_paperformat_args = {}

        return self._run_chrome(
            cr, uid, ids, report_name, context.get('landscape'),
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
    def _run_chrome(
        self, ids, report_name, landscape, paperformat,
        spec_paperformat_args=None, save_in_attachment=None,
        set_viewport_size=False
    ):
        if not save_in_attachment:
            save_in_attachment = {}

        chrome_port = self._get_chrome_port()

        # TODO viewport size
        # TODO use fd instead of port

        chrome_socket = None
        content = ''

        try:
            if not self._is_chrome_alive():
                cmd = [
                    self._get_chrome_bin()
                ] + self._get_chrome_flags() + filter(
                    None, self.env['ir.config_parameter'].get_param(
                        'report_qweb_chrome_renderer.chrome_extra_parameters',
                        ''
                    ).split(' ')
                )
                _logger.debug('starting %s', cmd)
                subprocess.Popen(cmd, close_fds=True)
                while not self._is_chrome_alive():
                    _logger.debug('waiting for chrome to start up')
                    time.sleep(.1)
                _logger.debug('chrome startup done')
            chrome_socket = CProto(LOCALHOST, chrome_port)
            chrome_socket.Page.enable()
            base_url = self.env['ir.config_parameter'].get_param(
                'report.url', self.env['ir.config_parameter'].get_param(
                    'web.base.url',
                )
            )
            chrome_socket.Network.setCookie(
                name='session_id',
                # in a test scenario, there's no request, so we pass some
                # session_id, as we only need a valid user anyways
                value=request and request.session.sid or
                root.session_store.list()[0],
                url=base_url,
            )

            lock = threading.Lock()
            lock.acquire()

            def on_load(dummy):
                lock.release()

            chrome_socket.Page.loadEventFired = on_load

            chrome_socket.Page.navigate(url='%s/report/html/%s/%s' % (
                base_url, report_name, ','.join(map(str, ids)),
            ))

            lock.acquire()
            content = chrome_socket.Page.printToPDF(
                landscape=bool(landscape),
                displayHeaderFooter=False,
                printBackground=True,
                scale=1.0,
                # they seriously use imperial units internally...
                paperWidth=paperformat.page_width / 25.4 or 8.5,
                paperHeight=paperformat.page_height / 25.4 or 11,
                marginTop=paperformat.margin_top / 25.4,
                marginBottom=paperformat.margin_bottom / 25.4,
                marginLeft=paperformat.margin_left / 25.4,
                marginRight=paperformat.margin_right / 25.4,
            )['result']['data']
            chrome_socket.Page.disable()

            chrome_socket.close()
            content = base64.b64decode(content)

        except:
            raise
        finally:
            if chrome_socket and chrome_socket.ws.connected:
                chrome_socket.close()

        return content

    @api.model
    def _get_chrome_bin(self):
        """Try to find some chrom{e,ium} binary"""
        result = False
        custom = self.env['ir.config_parameter'].get_param(
            'report_qweb_chrome_renderer.chrome_bin'
        )
        if custom:
            return custom
        for binary in [
                'chromium', 'chromium-browser', 'chrome',
                'google-chrome-stable',
        ]:
            try:
                result = find_in_path(binary)
            except IOError:
                pass
            if result:
                break
        return result

    @api.model
    def _get_chrome_flags(self):
        """Commandline switches to start chrome with"""
        return [
            '--headless',
            '--disable-gpu',
            '--remote-debugging-port={}'.format(self._get_chrome_port()),
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

    @api.model
    def _get_chrome_port(self):
        """Port for chrome to listen on"""
        return int(self.env['ir.config_parameter'].get_param(
            'report_qweb_chrome_renderer.chrome_port', 9222
        ))

    @api.model
    def _is_chrome_alive(self):
        """Check if there's something listening on port. Could be smarter"""
        return any(
            c for c in psutil.net_connections() if c.status == 'LISTEN' and
            c.laddr == (LOCALHOST, self._get_chrome_port())
        )
