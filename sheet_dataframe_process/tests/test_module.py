from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["try.file"]._populate()
        cls.env.ref(
            "sheet_dataframe_process.file_config_contact"
        ).populate_match_lines()
        cls.file_records = cls.env["try.file"].search([])

    def test_missing(self):
        wiz = self.get_wizard(self.file_records, "missing_required")
        self.assertTrue(wiz.partner_id)
        self.assertEqual(wiz.missing_cols, "['street']")

    def test_four_fields(self):
        wiz = self.get_wizard(self.file_records, "4_fields")
        self.assertFalse(wiz.missing_cols)

    def get_wizard(self, file_recs, file_str):
        action = file_recs.filtered(
            lambda s, file_str=file_str: file_str in s.name
        ).try_import()
        return self.env["sheet.dataframe.transient"].browse(action.get("res_id"))
