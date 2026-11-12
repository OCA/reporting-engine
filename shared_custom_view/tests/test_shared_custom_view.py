# Copyright 2026 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).
from odoo.tests import new_test_user
from odoo.tests.common import TransactionCase

BASE_ARCH = """<form string="My Dashboard">
    <board style="1">
        <column/>
    </board>
</form>"""


class TestSharedCustomView(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.board_view = cls.env["ir.ui.view"].create(
            {
                "name": "Test Board View",
                "model": "board.board",
                "type": "form",
                "arch": BASE_ARCH,
            }
        )

    def _custom_arch(self, marker):
        return f"""<form string="My Dashboard">
    <board style="1">
        <column>
            <action name="1" string="{marker}"/>
        </column>
    </board>
</form>"""

    def test_user_id_is_not_required(self):
        # this is the whole point of the module: a custom view without an
        # owner is what makes it "shared" between users
        custom_view = self.env["ir.ui.view.custom"].create(
            {
                "user_id": False,
                "ref_id": self.board_view.id,
                "arch": self._custom_arch("Shared"),
            }
        )
        self.assertFalse(custom_view.user_id)

    def test_get_view_falls_back_to_shared_custom_view(self):
        shared = self.env["ir.ui.view.custom"].create(
            {
                "user_id": False,
                "ref_id": self.board_view.id,
                "arch": self._custom_arch("Shared"),
            }
        )
        demo_user = new_test_user(
            self.env, login="shared_view_demo", groups="base.group_user"
        )
        result = (
            self.env["board.board"]
            .with_user(demo_user)
            .get_view(view_id=self.board_view.id, view_type="form")
        )
        self.assertEqual(result["custom_view_id"], shared.id)
        self.assertIn("Shared", result["arch"])

    def test_get_view_prefers_personal_over_shared_custom_view(self):
        self.env["ir.ui.view.custom"].create(
            {
                "user_id": False,
                "ref_id": self.board_view.id,
                "arch": self._custom_arch("Shared"),
            }
        )
        demo_user = new_test_user(
            self.env, login="shared_view_demo2", groups="base.group_user"
        )
        personal = self.env["ir.ui.view.custom"].create(
            {
                "user_id": demo_user.id,
                "ref_id": self.board_view.id,
                "arch": self._custom_arch("Personal"),
            }
        )
        result = (
            self.env["board.board"]
            .with_user(demo_user)
            .get_view(view_id=self.board_view.id, view_type="form")
        )
        self.assertEqual(result["custom_view_id"], personal.id)
        self.assertIn("Personal", result["arch"])

    def test_regular_user_can_open_a_board_with_a_shared_custom_view(self):
        """A plain internal user (no "Settings" access group) must be able
        to open a board view that falls back to a shared custom view.

        ``ir.ui.view.custom`` is only readable by ``base.group_system`` at
        the ir.model.access level (see odoo/addons/base/security/
        ir.model.access.csv), which is why core's own
        ``board.board.get_view()`` and the ``/board/add_to_dashboard``
        controller both use ``sudo()`` for it. ``board_board.py`` in this
        module does the same for its own lookups.
        """
        shared = self.env["ir.ui.view.custom"].create(
            {
                "user_id": False,
                "ref_id": self.board_view.id,
                "arch": self._custom_arch("Shared"),
            }
        )
        demo_user = new_test_user(
            self.env, login="shared_view_demo3", groups="base.group_user"
        )
        board = self.env["board.board"].with_user(demo_user)
        result = board.get_view(view_id=self.board_view.id, view_type="form")
        self.assertEqual(result["custom_view_id"], shared.id)
        self.assertIn("Shared", result["arch"])
