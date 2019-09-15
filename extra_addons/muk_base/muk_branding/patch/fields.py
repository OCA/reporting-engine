###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Branding 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import logging

from odoo import fields

from odoo.addons.muk_utils.tools.patch import monkey_patch
from odoo.addons.muk_branding.tools.debrand import safe_debrand

_logger = logging.getLogger(__name__)

@monkey_patch(fields._String)
def get_trans_func(self, records):
    if callable(self.translate):
        rec_src_trans = records.env['ir.translation']._get_terms_translations(self, records)
        def translate(record_id, value):
            src_trans = rec_src_trans[record_id]
            def debrand(source):
                trans = src_trans.get(source, source)
                if 'muk_branding.debranding' in records.env:
                    return records.env['muk_branding.debranding' ].debrand(trans)
                return trans
            return self.translate(debrand, value)
        return translate
    return get_trans_func.super(self, records)