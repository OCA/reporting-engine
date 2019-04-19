# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from odoo.tests.common import TransactionCase


class TestResPartner(TransactionCase):

    def setUp(self):
        super(TestResPartner, self).setUp()
        self.template_id = self.env['base.comment.template'].create({
            'name': 'Comment before lines',
            'position': 'before_lines',
            'text': 'Text before lines',
        })

    def test_commercial_partner_fields(self):
        # Azure Interior
        partner_id = self.env.ref('base.res_partner_12')
        partner_id.property_comment_template_id = self.template_id.id
        # Test childs propagation of commercial partner field
        for child_id in partner_id.child_ids:
            self.assertEqual(
                child_id.property_comment_template_id, self.template_id)
