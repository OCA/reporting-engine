# Copyright 2024 Quartile Limited (https://www.quartile.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class TestQwebFieldConverter(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.FloatConverter = cls.env["ir.qweb.field.float"]
        # Create a test currency record
        cls.test_currency = cls.env["res.currency"].create(
            {"name": "Test Currency", "symbol": "T", "rounding": 0.01}
        )
        # Create a test qweb field converter record
        cls.dp_qweb_rec = cls.env["qweb.field.converter"].create(
            {
                "res_model_id": cls.env.ref("base.model_res_currency").id,
                "field_id": cls.env["ir.model.fields"]
                ._get("res.currency", "rounding")
                .id,
                "digits": 0,
            }
        )

    def test_record_to_html(self):
        options = {}
        rendered_html = self.FloatConverter.record_to_html(
            self.test_currency, "rounding", options
        )
        self.assertEqual(rendered_html, "0")
        # Test with 2 digits
        self.dp_qweb_rec.digits = 2
        rendered_html = self.FloatConverter.record_to_html(
            self.test_currency, "rounding", options
        )
        self.assertEqual("0.01", rendered_html)
        # Test with 3 digits
        self.dp_qweb_rec.digits = 3
        rendered_html = self.FloatConverter.record_to_html(
            self.test_currency, "rounding", options
        )
        self.assertEqual("0.010", rendered_html)
        # Test without qweb field converter record (default is 6 digits)
        self.dp_qweb_rec.unlink()
        rendered_html = self.FloatConverter.record_to_html(
            self.test_currency, "rounding", options
        )
        self.assertEqual("0.010000", rendered_html)
