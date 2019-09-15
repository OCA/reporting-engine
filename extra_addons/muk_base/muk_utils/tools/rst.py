###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Utils 
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

from docutils import nodes
from docutils.core import publish_string
from docutils.transforms import Transform, writer_aux
from docutils.writers.html4css1 import Writer

from odoo import tools

_logger = logging.getLogger(__name__)

class ReStructuredTextFilterMessages(Transform):
    default_priority = 870
    def apply(self):
        for node in self.document.traverse(nodes.system_message):
            node.parent.remove(node)

class ReStructuredTextWriter(Writer):
    def get_transforms(self):
        return [ReStructuredTextFilterMessages, writer_aux.Admonitions]

def rst2html(content):
    overrides = {
        'embed_stylesheet': False,
        'doctitle_xform': False,
        'output_encoding': 'unicode',
        'xml_declaration': False,
    }
    output = publish_string(content, 
        settings_overrides=overrides,
        writer=ReStructuredTextWriter()
    )
    return tools.html_sanitize(output)
