# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):
    def setUp(self):
        super(TestResPartner, self).setUp()
        self.template_id = self.env["base.comment.template"].create(
            {
                "name": "Comment before lines",
                "position": "before_lines",
                "text": "<p>Text before lines</p>",
            }
        )

    def test_commercial_partner_fields(self):
        # Azure Interior
        partner_id = self.env.ref("base.res_partner_12")
        partner_id.property_comment_template_id = self.template_id.id
        # Test childs propagation of commercial partner field
        for child_id in partner_id.child_ids:
            self.assertEqual(child_id.property_comment_template_id, self.template_id)

    def test_get_value_without_partner(self):
        self.assertEqual(self.template_id.get_value(), "<p>Text before lines</p>")

    def test_get_value_with_partner(self):
        self.env["res.lang"]._activate_lang("fr_BE")
        partner = self.env.ref("base.res_partner_12")
        partner.write({"lang": "fr_BE"})
        self.template_id.with_context(lang="fr_BE").write(
            {"text": "<p>Testing translated fr_BE</p>"}
        )
        self.assertEqual(
            self.template_id.get_value(partner_id=partner.id),
            "<p>Testing translated fr_BE</p>",
        )
