###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Backend Theme 
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

from odoo import models, fields

class ResCompany(models.Model):
    
    _inherit = 'res.company'
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    background_image = fields.Binary(
        string="Apps Menu Background Image",
        attachment=True)
    
    background_blend_mode = fields.Selection(
        selection=[
            ('normal', 'Normal'),
            ('multiply', 'Multiply'),
            ('screen', 'Screen'),
            ('overlay', 'Overlay'),
            ('hard-light', 'Hard-light'),
            ('darken', 'Darken'),
            ('lighten', 'Lighten'),
            ('color-dodge', 'Color-dodge'),
            ('color-burn', 'Color-burn'),
            ('hard-light', 'Hard-light'),
            ('difference', 'Difference'),
            ('exclusion', 'Exclusion'),
            ('hue', 'Hue'),
            ('saturation', 'Saturation'),
            ('color', 'Color'),
            ('luminosity', 'Luminosity'),
        ], 
        string="Apps Menu Background Blend Mode",
        default='normal')
    
    default_sidebar_preference = fields.Selection(
        selection=[
            ('invisible', 'Invisible'),
            ('small', 'Small'),
            ('large', 'Large')
        ], 
        string="Sidebar Type",
        default='small')
    
    default_chatter_preference = fields.Selection(
        selection=[
            ('normal', 'Normal'),
            ('sided', 'Sided'),
        ], 
        string="Chatter Position", 
        default='sided')