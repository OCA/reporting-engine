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

import re
import uuid
import chardet

from itertools import chain
from lxml.etree import tostring
from lxml.html import fromstring

from odoo.tools import ustr

from odoo.addons.muk_utils.tools.utils import safe_execute

def debrand_documentation(text, value, expression):
    text = re.sub(
        r'https://www.{0}.com/documentation/'.format(expression),
        '{0}/documentation/'.format(value), text, flags=re.IGNORECASE
    )
    text = re.sub(
        r'https://www.{0}.com/page/docs/'.format(expression),
        '{0}/page/docs/'.format(value), text, flags=re.IGNORECASE
    )
    return text

def debrand_link(text, value, expression):
    text = re.sub(
        r'(http(s)?:\/\/)?(www.)?{0}.com'.format(expression),
        value, text, flags=re.IGNORECASE
    )
    return text

def debrand_text(text, value, expression):
    cases = {
        expression: uuid.uuid4().hex,
        expression.upper(): uuid.uuid4().hex,
        expression.lower(): uuid.uuid4().hex,
        expression.capitalize(): uuid.uuid4().hex,
    }
    def init_no_debranding(match):
        text = match.group()
        for key in cases:
            text = re.sub(r'\b{0}\b'.format(key), cases[key], text)
        return text
    def post_no_debranding(text):
        for key in cases:
            text = text.replace(cases[key], key)
        return text
    if isinstance(value, dict):
        text = safe_execute(text, debrand_documentation, text, value.get('documentation'), expression)
        text = safe_execute(text, debrand_link, text, value.get('website'), expression)
    text = re.sub(
        r'<.*class=".*no_debranding.*".*>.*(\b{0}\b).*<.*>'.format(expression),
        init_no_debranding, text, flags=re.IGNORECASE
    )
    text = re.sub(
        r'\b(?<!\.){0}(?!\.\S|\s?=|\w|\[)\b'.format(expression),
        value.get('system_name') if isinstance(value, dict) else value,
        text, flags=re.IGNORECASE
    )
    return post_no_debranding(text)

def debrand_with_check(text, value, expression):
    if not text or not re.search(r'\b{0}\b'.format(expression), text, re.IGNORECASE):
        return text
    return debrand_text(text, value, expression)

def debrand(input, value, expression="odoo"):
    if isinstance(input, str):
        return ustr(debrand_with_check(input, value, expression)) 
    if isinstance(input, bytes):
        encoding = chardet.detect(input)['encoding'] or 'utf-8'
        return bytes(debrand(ustr(input, hint_encoding=encoding), value, expression), encoding)
    return input

def safe_debrand(input, value, expression="odoo"):
    return safe_execute(input, debrand, input, value, expression)
