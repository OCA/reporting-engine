# -*- coding: utf-8 -*-
##############################################################################
#
# Odoo, an open source suite of business apps
# This module copyright (C) 2015 bloopark systems (<http://bloopark.de>).
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.addons.report.controllers.main import ReportController
from openerp.addons.web.http import route, request

import cStringIO
import re

from werkzeug import exceptions

try:
    from elaphe import barcode
except Exception:
    pass


class ReportBarcodeController(ReportController):

    """The class of Report controller"""

    @route()
    def report_barcode(self, type, value, width=0, height=0,
                       humanreadable=0, **kw):
        """Contoller able to render barcode images thanks to elaphe.
        Samples:
            <img t-att-src="'/report/barcode/QR/%s' % o.name"/>
            <img t-att-src="'/report/barcode?type=%s&amp;value=%s&amp;width=%s&amp;height=%s' %
                ('QR', o.name, 200, 200)"/>

        :param type: Accepted types: 'auspost', 'azteccode', 'codabar',
        'code11', 'code128', 'code25', 'code39', 'code93', 'datamatrix', 'ean',
        'i2of5', 'japanpost', 'kix', 'maxicode', 'msi', 'onecode', 'pdf417',
        'pharmacode', 'plessey', 'postnet', 'qrcode', 'royalmail', 'rss14',
        'symbol', 'upc'
        :param barmargin: Accepted positive integer values
        :param width: Accepted positive integer values
        :param height: Accepted positive integer values
        :param scale: Accepted positive float values
        :param extraopts: Accepted different params per type of barcode. Eg: extraopts='{eclevel:M,version:8}'
        """
        try:
            width, height, scale, margin = int(width), int(height), float(
                kw.get('scale', 2.0)), int(kw.get('barmargin', 0))
            opts = {}

            try:
                extra_opts = {}
                if kw.get('extraopts', False):
                    for opt in kw['extraopts'].split(','):
                        key = opt.split(':')[0]
                        if opt.split(':')[1] == 'True':
                            values = True
                        elif opt.split(':')[1] == 'False':
                            values = False
                        elif opt.split(':')[1].isdigit():
                            values = int(opt.split(':')[1])
                        elif re.match("^\d+?\.\d+?$", opt.split(':')[1]):
                            values = float(opt.split(':')[1])
                        else:
                            values = opt.split(':')[1]
                        extra_opts[key] = values
                    opts.update(extra_opts)
            except IndexError:
                pass

            barcode_out = cStringIO.StringIO()
            barcode_img = barcode(type, str(value), opts, scale=scale,
                                  margin=margin)
            if width and height:
                barcode_img = barcode_img.resize((width, height))
            barcode_img.save(barcode_out, "png", resolution=100.0)

        except (ValueError, AttributeError):
            raise exceptions.HTTPException(
                description='Cannot convert into barcode.')

        return request.make_response(barcode_out.getvalue(),
                                     headers=[('Content-Type', 'image/png')])