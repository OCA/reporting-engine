###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Converter 
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
import textwrap

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    converter_service = fields.Selection(
        selection=[
            ("unoconv", "Local"),
            ("provider", "Service")],
        string="Converter",
        default="provider",
        help=textwrap.dedent("""\
            Converter engine, which is used for the conversion:
            - Local: Use a locally installed unoconv installation
            - Service: Use a service to do the conversion
            """))

    converter_max_store = fields.Integer(
        string="Storage Size",
        help=textwrap.dedent("""\
            To certify the conversion, converted files can be saved
            and loaded from memory if necessary. You can set a maximum
            size of the storage to prevent massive memory requirements.
            """))
    
    converter_credit = fields.Boolean(
        compute='_compute_converter_credit',
        string="Converter insufficient credit")

    @api.multi 
    def set_values(self):
        res = super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        param.set_param("muk_converter.service", self.converter_service)
        param.set_param("muk_converter.max_store", self.converter_max_store)
        return res

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        res.update(
            converter_service=params.get_param("muk_converter.service", default="provider"),
            converter_max_store=int(params.get_param("muk_converter.max_store", default=20))
        )
        return res
    
    @api.multi
    def _compute_converter_credit(self):
        credits = self.env['iap.account'].get_credits('muk_converter')
        for record in self:
            record.converter_credit = credits <= 0
    @api.multi
    def redirect_to_buy_converter_credit(self):
        url = self.env['iap.account'].get_credits_url('muk_converter')
        return {
            'type': 'ir.actions.act_url',
            'url': url,
            'target': '_new',
        }
