# Copyright 2026 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import ast
import datetime

from dateutil.relativedelta import relativedelta
from lxml import etree

from odoo.tests.common import TransactionCase


class TestBoardEvalContext(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.board = cls.env["board.board"]

    def _get_action_domain(self, arch):
        action_node = etree.fromstring(arch).xpath("//action")[0]
        return ast.literal_eval(action_node.get("domain"))

    def test_get_eval_context_keys(self):
        eval_context = self.board._get_eval_context()
        self.assertEqual(eval_context["uid"], self.env.uid)
        self.assertIs(eval_context["date"], datetime.date)
        self.assertIs(eval_context["datetime"], datetime.datetime)
        self.assertIs(eval_context["timedelta"], datetime.timedelta)
        self.assertIs(eval_context["timezone"], datetime.timezone)
        self.assertIs(eval_context["tzinfo"], datetime.tzinfo)
        self.assertIs(eval_context["relativedelta"], relativedelta)

    def test_arch_preprocessing_evaluates_uid_in_domain(self):
        arch = """<form string="My Dashboard">
    <board style="1">
        <column>
            <action name="1" string="Something" domain="[('id', '=', uid)]"/>
        </column>
    </board>
</form>"""
        result = self.board._arch_preprocessing(arch)
        self.assertEqual(self._get_action_domain(result), [("id", "=", self.env.uid)])

    def test_arch_preprocessing_evaluates_relativedelta_in_domain(self):
        expected = (datetime.date.today() - relativedelta(days=7)).isoformat()
        domain_expr = (
            "[('date', '>=', (date.today() - relativedelta(days=7)).isoformat())]"
        )
        arch = f"""<form string="My Dashboard">
    <board style="1">
        <column>
            <action name="1" string="Something" domain="{domain_expr}"/>
        </column>
    </board>
</form>"""
        result = self.board._arch_preprocessing(arch)
        self.assertEqual(self._get_action_domain(result), [("date", ">=", expected)])

    def test_arch_preprocessing_keeps_static_domain(self):
        arch = """<form string="My Dashboard">
    <board style="1">
        <column>
            <action name="1" string="Something" domain="[('active', '=', True)]"/>
        </column>
    </board>
</form>"""
        result = self.board._arch_preprocessing(arch)
        self.assertEqual(self._get_action_domain(result), [("active", "=", True)])

    def test_arch_preprocessing_ignores_action_without_domain(self):
        arch = """<form string="My Dashboard">
    <board style="1">
        <column>
            <action name="1" string="Something"/>
        </column>
    </board>
</form>"""
        # must not raise, an action without a domain is simply left untouched
        result = self.board._arch_preprocessing(arch)
        action_node = etree.fromstring(result).xpath("//action")[0]
        self.assertIsNone(action_node.get("domain"))

    def test_arch_preprocessing_evaluates_nested_domain(self):
        # fix_domain() recurses through arbitrarily nested containers,
        # not only direct children of <column>
        arch = """<form string="My Dashboard">
    <board style="1">
        <column>
            <group>
                <action name="1" string="Something" domain="[('id', '=', uid)]"/>
            </group>
        </column>
    </board>
</form>"""
        result = self.board._arch_preprocessing(arch)
        self.assertEqual(self._get_action_domain(result), [("id", "=", self.env.uid)])
