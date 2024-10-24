from lxml import etree

from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env["df.source"]._populate()
        cls.file_records = cls.env["df.source"].search([])

    def test_missing_required_column(self):
        wiz = self.get_wizard(self.file_records, "missing_required_column")
        comment = sanitize(str(wiz.comment))
        root = etree.fromstring(comment)
        self.assertEqual(
            root.xpath('//div[@id="missing-columns-data"]')[0].text,
            "['Street']",
        )

    def test_four_fields(self):
        wiz = self.get_wizard(self.file_records, "4_fields")
        comment = sanitize(str(wiz.comment))
        root = etree.fromstring(comment)
        self.assertEqual(
            len(root.xpath('//div[@id="missing-values-in-name"]')),
            1,
            "Missing value in Name column",
        )
        self.assertEqual(
            len(root.xpath('//div[@id="missing-values-in-street"]')),
            1,
            "Missing values in Street column",
        )

    def get_wizard(self, source_recs, file_str):
        source = source_recs.filtered(lambda s, file_str=file_str: file_str in s.name)
        action = source.start()
        return self.env["df.process.wiz"].browse(action.get("res_id"))


def sanitize(string):
    string = string.replace("<br>", "<br />")
    return string
