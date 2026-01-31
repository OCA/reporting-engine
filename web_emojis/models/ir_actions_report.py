# Copyright 2026 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from emoji_data_python import get_emoji_regex
from twemoji_api import get_emoji_url

from odoo import models

_logger = logging.getLogger(__name__)


def _emoji_to_img(match):
    """Replace an emoji match with an img tag."""
    emoji = match.group(0)
    try:
        url = get_emoji_url(emoji)
    except ValueError:
        return emoji
    # flake8: noqa
    return (
        f'<img src="{url}" alt="{emoji}" '
        f'style="height: 1em; width: 1em; vertical-align: -0.1em;">'
    )


def replace_emojis(html):
    """Replace emojis in HTML with Twemoji img tags."""
    if not html:
        return html
    return get_emoji_regex().sub(_emoji_to_img, html)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        bodies = [replace_emojis(body) for body in bodies]
        # headers and footers are already problematic enough
        # if header:
        #     header = replace_emojis(header)
        # if footer:
        #     footer = replace_emojis(footer)
        return super()._run_wkhtmltopdf(
            bodies,
            report_ref=report_ref,
            header=header,
            footer=footer,
            landscape=landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
