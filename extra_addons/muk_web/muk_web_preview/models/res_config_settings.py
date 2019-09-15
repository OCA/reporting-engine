###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Preview 
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

from odoo import api, fields, models

class ResConfigSettings(models.TransientModel):

    _inherit = 'res.config.settings'

    module_muk_web_preview_audio = fields.Boolean(
        string="Preview Audio",
        help="Extendes the Preview Dialog to support audio.")
    
    module_muk_web_preview_csv = fields.Boolean(
        string="Preview CSV",
        help="Extendes the Preview Dialog to support csv files.")
    
    module_muk_web_preview_image = fields.Boolean(
        string="Preview Image",
        help="Extendes the Preview Dialog to support image files.")
    
    module_muk_web_preview_mail = fields.Boolean(
        string="Preview Mail",
        help="Extendes the Preview Dialog to support mails.")
    
    module_muk_web_preview_markdown = fields.Boolean(
        string="Preview Markdown",
        help="Extendes the Preview Dialog to support markdown files.")
    
    module_muk_web_preview_msoffice = fields.Boolean(
        string="Preview MS Office",
        help="Extendes the Preview Dialog to support office files.")
    
    module_muk_web_preview_opendocument = fields.Boolean(
        string="Preview Open Document",
        help="Extendes the Preview Dialog to support open document files.")
    
    module_muk_web_preview_rst = fields.Boolean(
        string="Preview ReStructuredText",
        help="Extendes the Preview Dialog to support reStructuredText.")
    
    module_muk_web_preview_text = fields.Boolean(
        string="Preview Text",
        help="Extendes the Preview Dialog to support text files.")
    
    module_muk_web_preview_video = fields.Boolean(
        string="Preview Video",
        help="Extendes the Preview Dialog to support video files.")