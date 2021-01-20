# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

import html
import logging
import time
from base64 import b64decode

from odoo.tools import mail, misc

logger = logging.getLogger(__name__)

try:
    from genshi.core import Markup
except ImportError:
    logger.debug("Cannot import py3o.template")


def format_multiline_value(value):
    if value:
        return Markup(
            html.escape(value)
            .replace("\n", "<text:line-break/>")
            .replace("\t", "<text:s/><text:s/><text:s/><text:s/>")
        )
    return ""


def display_address(address_record, without_company=False):
    return address_record.display_address(without_company=without_company)


class Py3oParserContext(object):
    def __init__(self, env):
        self._env = env

        self.localcontext = {
            "user": self._env.user,
            "lang": self._env.lang,
            # Odoo default format methods
            "o_format_lang": self._format_lang,
            # prefixes with o_ to avoid nameclash with default method provided
            # by py3o.template
            "o_format_date": self._format_date,
            # give access to the time lib
            "time": time,
            # keeps methods from report_sxw to ease migration
            "display_address": display_address,
            "formatLang": self._old_format_lang,
            "format_multiline_value": format_multiline_value,
            "html_sanitize": mail.html2plaintext,
            "b64decode": b64decode,
        }

    def _format_lang(
        self,
        value,
        lang_code=False,
        digits=None,
        grouping=True,
        monetary=False,
        dp=False,
        currency_obj=False,
        no_break_space=True,
    ):
        env = self._env
        if lang_code:
            context = dict(env.context, lang=lang_code)
            env = env(context=context)
        formatted_value = misc.formatLang(
            env,
            value,
            digits=digits,
            grouping=grouping,
            monetary=monetary,
            dp=dp,
            currency_obj=currency_obj,
        )
        if currency_obj and currency_obj.symbol and no_break_space:
            parts = []
            if currency_obj.position == "after":
                parts = formatted_value.rsplit(" ", 1)
            elif currency_obj and currency_obj.position == "before":
                parts = formatted_value.split(" ", 1)
            if parts:
                formatted_value = "\N{NO-BREAK SPACE}".join(parts)
        return formatted_value

    def _format_date(self, value, lang_code=False, date_format=False):
        return misc.format_date(
            self._env, value, lang_code=lang_code, date_format=date_format
        )

    def _old_format_lang(
        self,
        value,
        digits=None,
        date=False,
        date_time=False,
        grouping=True,
        monetary=False,
        dp=False,
        currency_obj=False,
    ):
        """
        :param value: The value to format
        :param digits: Number of digits to display by default
        :param date: True if value must be formatted as a date (default False)
        :param date_time: True if value must be formatted as a datetime
                          (default False)
        :param grouping: If value is float and grouping is True, the value will
                         be formatted with the appropriate separators between
                         figures according to the current lang specifications
        :param monetary: If value is float and monetary is True and grouping is
                         True the value will be formatted according to the
                         monetary format defined for the current lang
        :param dp: Decimal precision
        :param currency_obj: If provided the currency symbol will be added to
                             value at position defined by the currency object
        :return: The formatted value
        """
        if not date and not date_time:
            return self._format_lang(
                value,
                digits=digits,
                grouping=grouping,
                monetary=monetary,
                dp=dp,
                currency_obj=currency_obj,
                no_break_space=True,
            )

        return self._format_date(value)
