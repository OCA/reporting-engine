# -*- coding: utf-8 -*-
# Copyright 2015 bloopark systems (<http://bloopark.de>).
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import models
from openerp.tools.safe_eval import safe_eval as eval

import cStringIO
import re

try:
    from elaphe import barcode
except ImportError:
    pass


class Report(models.Model):
    _inherit = 'report'

    def generate_barcode(self, type, value, kw, width=0, height=0):
        width = int(width)
        height = int(height)
        scale = float(kw.get('scale', 2.0))
        margin = float(kw.get('barmargin', 0))
        extra_opts = {}
        barcode_out = cStringIO.StringIO()
        if kw.get('extraopts', False):
            for opt in kw['extraopts'].split(','):
                key = opt.split(':')[0]
                values = opt.split(':')[1]
                if re.search(r'^(?:[0-9a-fA-F]{3}){1,2}$', values) is None:
                    values = eval(values)
                extra_opts[key] = values
        try:
            barcode_img = barcode(type, str(value), extra_opts, scale=scale,
                                  margin=margin)
            if width and height:
                barcode_img = barcode_img.resize((width, height))
            barcode_img.save(barcode_out, "png", resolution=100.0)
        except (ValueError, AttributeError):
            raise ValueError('Cannot convert into barcode.')

        return barcode_out.getvalue()