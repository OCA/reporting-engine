# Copyright 2025 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestReportPartnerAddress(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ja = (
            cls.env["res.lang"]
            .with_context(active_test=False)
            .search([("code", "=", "ja_JP")])
        )
        cls.env["base.language.install"].create({"lang_ids": [ja.id]}).lang_install()
        cls.partner = cls.env["res.partner"].create(
            {
                "name": "Test Company",
                "street": "1-2-3 Jingumae",
                "city": "Shibuya-ku, Tokyo",
                "zip": "150-0001",
                "country_id": cls.env.ref("base.jp").id,
            }
        )
        # Japanese address format (native)
        cls.partner.with_context(lang="ja_JP").write(
            {"address_details": "〒150-0001\n東京都渋谷区神宮前1-2-3\nテスト株式会社"}
        )
        # English transliteration for international use
        cls.partner.address_details = (
            "Test Company\n1-2-3 Jingumae, Shibuya-ku\nTokyo 150-0001\nJapan"
        )

    def test_address_details_always_used(self):
        res = self.partner.with_context(lang="en_US")._display_address()
        self.assertEqual(
            res, "Test Company\n1-2-3 Jingumae, Shibuya-ku\nTokyo 150-0001\nJapan"
        )
        res = self.partner.with_context(lang="ja_JP")._display_address()
        self.assertEqual(res, "〒150-0001\n東京都渋谷区神宮前1-2-3\nテスト株式会社")

    def test_address_details_empty_uses_standard_format(self):
        partner = self.env["res.partner"].create(
            {
                "name": "No Details Partner",
                "street": "123 Main St",
                "city": "Springfield",
                "zip": "12345",
                "country_id": self.env.ref("base.us").id,
            }
        )
        res = partner._display_address()
        self.assertIn("123 Main St", res)
        self.assertIn("Springfield", res)

    def test_contact_inherits_address_details_from_parent(self):
        contact = self.env["res.partner"].create(
            {"name": "Contact Person", "type": "contact", "parent_id": self.partner.id}
        )
        self.assertEqual(
            contact.address_details,
            "Test Company\n1-2-3 Jingumae, Shibuya-ku\nTokyo 150-0001\nJapan",
        )
        self.assertEqual(
            contact.with_context(lang="ja_JP").address_details,
            "〒150-0001\n東京都渋谷区神宮前1-2-3\nテスト株式会社",
        )

    def test_non_contact_does_not_inherit_address_details(self):
        delivery_address = self.env["res.partner"].create(
            {
                "name": "Delivery Address",
                "type": "delivery",
                "parent_id": self.partner.id,
                "street": "456 Delivery St",
            }
        )
        # Non-contact address should NOT inherit parent's address_details
        self.assertFalse(delivery_address.address_details)
