# Copyright 2021-2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import datetime

from dateutil.relativedelta import relativedelta

from odoo import api, models
from odoo.tools.safe_eval import safe_eval


class Board(models.AbstractModel):
    _inherit = "board.board"

    def _get_eval_context(self):
        """Prepare the context used when evaluating python code
        :returns: dict -- evaluation context given to safe_eval
        """
        return {
            "datetime": datetime.datetime,
            "date": datetime.date,
            "timedelta": datetime.timedelta,
            "timezone": datetime.timezone,
            "tzinfo": datetime.tzinfo,
            "relativedelta": relativedelta,
            "uid": self.env.uid,
        }

    @api.model
    def _arch_preprocessing(self, arch):
        # keeping it inside the method as in the
        # original code, for perf reason at startup
        from lxml import etree

        arch = super()._arch_preprocessing(arch)
        eval_context = self._get_eval_context()

        def fix_domain(node):
            for child in node.iterchildren():
                if child.tag == "action" and child.get("domain"):
                    domain = safe_eval(child.get("domain"), eval_context)
                    child.set("domain", str(domain))
                else:
                    fix_domain(child)
            return node

        archnode = etree.fromstring(arch)
        archnode = fix_domain(archnode)
        return etree.tostring(archnode, pretty_print=True, encoding="unicode")
