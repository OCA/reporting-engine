# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import re
import time
from datetime import datetime

import odoo
from odoo import fields
from odoo.tools import (
    DEFAULT_SERVER_DATE_FORMAT,
    DEFAULT_SERVER_DATETIME_FORMAT)

odt_namespace = {
    "office": "{urn:oasis:names:tc:opendocument:xmlns:office:1.0}",
    "style": "{urn:oasis:names:tc:opendocument:xmlns:style:1.0}",
    "text": "{urn:oasis:names:tc:opendocument:xmlns:text:1.0}",
    "table": "{urn:oasis:names:tc:opendocument:xmlns:table:1.0}",
    "draw": "{urn:oasis:names:tc:opendocument:xmlns:drawing:1.0}",
    "fo": "{urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0}",
    "xlink": "{http://www.w3.org/1999/xlink}",
    "dc": "{http://purl.org/dc/elements/1.1/}",
    "meta": "{urn:oasis:names:tc:opendocument:xmlns:meta:1.0}",
    "number": "{urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0}",
    "svg": "{urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0}",
    "chart": "{urn:oasis:names:tc:opendocument:xmlns:chart:1.0}",
    "dr3d": "{urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0}",
    "math": "{http://www.w3.org/1998/Math/MathML}",
    "form": "{urn:oasis:names:tc:opendocument:xmlns:form:1.0}",
    "script": "{urn:oasis:names:tc:opendocument:xmlns:script:1.0}",
    "ooo": "{http://openoffice.org/2004/office}",
    "ooow": "{http://openoffice.org/2004/writer}",
    "oooc": "{http://openoffice.org/2004/calc}",
    "dom": "{http://www.w3.org/2001/xml-events}"}

sxw_namespace = {
    "office": "{http://openoffice.org/2000/office}",
    "style": "{http://openoffice.org/2000/style}",
    "text": "{http://openoffice.org/2000/text}",
    "table": "{http://openoffice.org/2000/table}",
    "draw": "{http://openoffice.org/2000/drawing}",
    "fo": "{http://www.w3.org/1999/XSL/Format}",
    "xlink": "{http://www.w3.org/1999/xlink}",
    "dc": "{http://purl.org/dc/elements/1.1/}",
    "meta": "{http://openoffice.org/2000/meta}",
    "number": "{http://openoffice.org/2000/datastyle}",
    "svg": "{http://www.w3.org/2000/svg}",
    "chart": "{http://openoffice.org/2000/chart}",
    "dr3d": "{http://openoffice.org/2000/dr3d}",
    "math": "{http://www.w3.org/1998/Math/MathML}",
    "form": "{http://openoffice.org/2000/form}",
    "script": "{http://openoffice.org/2000/script}",
    "ooo": "{http://openoffice.org/2004/office}",
    "ooow": "{http://openoffice.org/2004/writer}",
    "oooc": "{http://openoffice.org/2004/calc}",
    "dom": "{http://www.w3.org/2001/xml-events}"}

_logger = logging.getLogger(__name__)

rml_parents = {
    'tr': 1,
    'li': 1,
    'story': 0,
    'section': 0
}

rml_tag = "para"

sxw_parents = {
    'table-row': 1,
    'list-item': 1,
    'body': 0,
    'section': 0,
}

html_parents = {
    'tr': 1,
    'body': 0,
    'div': 0
    }
sxw_tag = "p"

rml2sxw = {
    'para': 'p',
}


def get_date_length(date_format=DEFAULT_SERVER_DATE_FORMAT):
    return len((datetime.now()).strftime(date_format))


class RMLParse(object):
    def __init__(self, cr, uid, name, parents=rml_parents,
                 tag=rml_tag, context=None):
        if not context:
            context = {}
        self.cr = cr
        self.uid = uid
        env = odoo.api.Environment(cr, uid, context)
        user = env['res.users'].browse(uid)
        self.localcontext = {
            'user': user,
            'setCompany': self.set_company,
            'repeatIn': self.repeat_in,
            'setLang': self.set_lang,
            'setTag': self.set_tag,
            'removeParentNode': self.remove_parent_node,
            'format': self.format,
            'formatLang': self.format_lang,
            'lang': user.company_id.partner_id.lang,
            'translate': self._translate,
            'setHtmlImage': self.set_html_image,
            'strip_name': self._strip_name,
            'time': time,
            'display_address': self.display_address,
            # more context members are setup in setCompany() below:
            #  - company_id
            #  - logo
        }
        self.set_company(user.company_id)
        self.localcontext.update(context)
        self.name = name
        self._node = None
        self.parents = parents
        self.tag = tag
        self._lang_cache = {}
        self.lang_dict = {}
        self.default_lang = {}
        self.lang_dict_called = False
        self._transl_regex = re.compile(r'(\[\[.+?\]\])')

    def set_tag(self, oldtag, newtag, attrs=None):
        return newtag, attrs

    def _ellipsis(self, char, size=100, truncation_str='...'):
        if not char:
            return ''
        if len(char) <= size:
            return char
        return char[:size-len(truncation_str)] + truncation_str

    def set_company(self, company_id):
        if company_id:
            self.localcontext['company'] = company_id
            self.localcontext['logo'] = company_id.logo
            self.header = company_id.report_header
            self.logo = company_id.logo

    def _strip_name(self, name, maxlen=50):
        return self._ellipsis(name, maxlen)

    def format(self, text, oldtag=None):
        return text.strip()

    def remove_parent_node(self, tag=None):
        raise GeneratorExit('Skip')

    def set_html_image(self, id, model=None, field=None, context=None):
        if not id:
            return ''
        if not model:
            model = 'ir.attachment'
        try:
            env = odoo.api.Environment(self.cr, self.uid, {})
            res = env[model].browse(int(id)).read()[0]
            if field:
                return res[field]
            elif model == 'ir.attachment':
                return res['datas']
            else:
                return ''
        except Exception:
            return ''

    def set_lang(self, lang):
        self.localcontext['lang'] = lang
        self.lang_dict_called = False
        # re-evaluate self.objects in a different environment
        env = self.objects.env(self.cr, self.uid, self.localcontext)
        self.objects = self.objects.with_env(env)

    def _get_lang_dict(self):
        env = odoo.api.Environment(self.cr, self.uid, {})
        env_lang = env['res.lang']
        lang = self.localcontext.get('lang', 'en_US') or 'en_US'
        lang_obj = env_lang.search([('code', '=', lang)], limit=1) or \
            env_lang.search([('code', '=', 'en_US')])
        self.lang_dict.update({'lang_obj': lang_obj,
                               'date_format': lang_obj.date_format,
                               'time_format': lang_obj.time_format})
        self.default_lang[lang] = self.lang_dict.copy()
        return True

    def digits_fmt(self, obj=None, f=None, dp=None):
        digits = self.get_digits(obj, f, dp)
        return "%%.%df" % (digits, )

    def get_digits(self, obj=None, f=None, dp=None):
        d = DEFAULT_DIGITS = 2
        if dp:
            env = odoo.api.Environment(self.cr, self.uid, {})
            d = env['decimal.precision'].precision_get(dp)
        elif obj and f:
            res_digits = getattr(obj._fields[f], 'digits',
                                 lambda x: (16, DEFAULT_DIGITS))
            if isinstance(res_digits, tuple):
                d = res_digits[1]
            else:
                d = res_digits(self.cr)[1]
        elif hasattr(obj, '_field') and \
                obj._field.type == 'float' and \
                obj._field.digits:
                d = obj._field.digits[1]
                if not d and d is not 0:
                    d = DEFAULT_DIGITS
        return d

    def format_lang(self, value, digits=None, date=False,
                    date_time=False, grouping=True, monetary=False,
                    dp=False, currency_obj=False):
        if digits is None:
            if dp:
                digits = self.get_digits(dp=dp)
            elif currency_obj:
                digits = currency_obj.decimal_places
            else:
                digits = self.get_digits(value)

        if isinstance(value, str) and not value:
            return ''

        if not self.lang_dict_called:
            self._get_lang_dict()
            self.lang_dict_called = True

        if date or date_time:
            if not value:
                return ''

            date_format = self.lang_dict['date_format']
            parse_format = DEFAULT_SERVER_DATE_FORMAT
            if date_time:
                value = value.split('.')[0]
                date_format = date_format + " " +\
                    self.lang_dict['time_format']
                parse_format = DEFAULT_SERVER_DATETIME_FORMAT
            if isinstance(value, (str, bytes)):
                # FIXME: the trimming is probably unreliable
                # if format includes day/month names
                # and those would need to be translated anyway.
                date = datetime.strptime(
                    value[:get_date_length(parse_format)], parse_format)
            elif isinstance(value, time.struct_time):
                date = datetime(*value[:6])
            else:
                date = datetime(*value.timetuple()[:6])
            if date_time:
                # Convert datetime values
                # to the expected client/context timezone
                env = odoo.api.Environment(self.cr, self.uid, {})
                record = env['base'].with_context(self.localcontext)
                date = fields.Datetime.context_timestamp(record, date)
            return date.strftime(date_format.encode('utf-8'))

        res = self.lang_dict['lang_obj'].format(
            '%.' + str(digits) + 'f', value,
            grouping=grouping, monetary=monetary)
        if currency_obj and currency_obj.symbol:
            if currency_obj.position == 'after':
                res = u'%s\N{NO-BREAK SPACE}%s' % (res, currency_obj.symbol)
            elif currency_obj and currency_obj.position == 'before':
                res = u'%s\N{NO-BREAK SPACE}%s' % (currency_obj.symbol, res)
        return res

    def display_address(self, address_record, without_company=False):
        # FIXME handle `without_company`
        return address_record.contact_address

    def repeat_in(self, lst, name, nodes_parent=False):
        ret_lst = []
        for id in lst:
            ret_lst.append({name: id})
        return ret_lst

    def _translate(self,text):
        lang = self.localcontext['lang']
        if lang and text and not text.isspace():
            env = odoo.api.Environment(self.cr, self.uid, {})
            Translation = env['ir.translation']
            piece_list = self._transl_regex.split(text)
            for pn in range(len(piece_list)):
                if not self._transl_regex.match(piece_list[pn]):
                    source_string = piece_list[pn].replace('\n', ' ').strip()
                    if len(source_string):
                        translated_string = Translation._get_source(
                            self.name, ('report', 'rml'), lang, source_string)
                        if translated_string:
                            piece_list[pn] = piece_list[pn].replace(
                                source_string, translated_string)
            text = ''.join(piece_list)
        return text

    def set_context(self, objects, data, ids, report_type=None):
        self.localcontext['data'] = data
        self.localcontext['objects'] = objects
        self.localcontext['digits_fmt'] = self.digits_fmt
        self.localcontext['get_digits'] = self.get_digits
        self.datas = data
        self.ids = ids
        self.objects = objects
        if report_type:
            if report_type=='odt' :
                self.localcontext.update({'name_space': odt_namespace})
            else:
                self.localcontext.update({'name_space': sxw_namespace})

        # WARNING: the object[0].exists() call below
        # is slow but necessary because
        # some broken reporting wizards
        # pass incorrect IDs (e.g. ir.ui.menu ids)
        if objects and len(objects) == 1 and \
            objects[0].exists() and \
                'company_id' in objects[0] and objects[0].company_id:
            # When we print only one record, we can auto-set the correct
            # company in the localcontext. For other cases the report
            # will have to call setCompany() inside the main repeatIn loop.
            self.set_company(objects[0].company_id)
