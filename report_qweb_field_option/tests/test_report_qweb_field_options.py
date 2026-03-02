# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.exceptions import ValidationError
from odoo.orm.model_classes import add_to_registry
from odoo.tests.common import TransactionCase


class TestQwebFieldOptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        from .test_models import TestQwebFieldModel

        add_to_registry(cls.registry, TestQwebFieldModel)
        cls.registry._setup_models__(cls.env.cr, ["test.qweb.field.options"])
        cls.registry.init_models(
            cls.env.cr, ["test.qweb.field.options"], {"models_to_check": True}
        )
        cls.addClassCleanup(cls.registry.__delitem__, "test.qweb.field.options")
        cls.test_model = cls.env["ir.model"]._get("test.qweb.field.options")
        cls.quantity_field = cls.env["ir.model.fields"]._get(
            "test.qweb.field.options", "quantity"
        )
        cls.uom_field = cls.env["ir.model.fields"]._get(
            "test.qweb.field.options", "uom_id"
        )
        cls.value_field = cls.env["ir.model.fields"]._get(
            "test.qweb.field.options", "value"
        )
        cls.currency_field = cls.env["ir.model.fields"]._get(
            "test.qweb.field.options", "currency_id"
        )
        cls.IrQweb = cls.env["ir.qweb"]
        cls.test_currency = cls.env["res.currency"].create(
            {"name": "Test Currency", "symbol": "$"}
        )
        cls.unit_uom = cls.env.ref("uom.product_uom_unit")
        cls.test_record = cls.env["test.qweb.field.options"].create(
            {
                "name": "Test",
                "quantity": 1.00,
                "value": 1.00,
                "currency_id": cls.test_currency.id,
                "company_id": cls.env.company.id,
            }
        )
        cls.qweb_options_rec = cls.env["qweb.field.options"].create(
            {
                "res_model_id": cls.test_model.id,
                "field_id": cls.value_field.id,
                "currency_id": cls.test_currency.id,
                "currency_field_id": cls.currency_field.id,
                "digits": 0,
            }
        )
        cls.env["qweb.field.options"].create(
            {
                "res_model_id": cls.test_model.id,
                "field_id": cls.quantity_field.id,
                "uom_id": cls.unit_uom.id,
                "uom_field_id": cls.uom_field.id,
                "digits": 3,
            }
        )

    def test_qweb_field_option(self):
        values = {"report_type": "pdf"}
        # Test with 0 digits
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertEqual(content, "1")

        # Test with 2 digits
        self.qweb_options_rec.digits = 2
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertEqual(content, "1.00")

        # Test with 3 digits
        self.qweb_options_rec.digits = 3
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertEqual(content, "1.000")

        # Test with widget
        self.qweb_options_rec.field_options = "{'widget': 'monetary'}"
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertIn("$", content)

        # Test that an error is raised when the input value is incorrect.
        with self.assertRaises(ValidationError):
            self.qweb_options_rec.field_options = (
                "{'widget': 'monetary', 'currency_field': self.test_record}"
            )

        with self.assertRaises(ValidationError):
            self.qweb_options_rec.field_options = "'widget': 'monetary'"

    def test_qweb_field_option_with_multiple_record(self):
        values = {"report_type": "pdf"}
        qweb_options_company_rec = self.env["qweb.field.options"].create(
            {
                "res_model_id": self.test_model.id,
                "field_id": self.value_field.id,
                "currency_id": self.test_currency.id,
                "currency_field_id": self.currency_field.id,
                "company_id": self.env.company.id,
                "digits": 1,
            }
        )

        # If there are two records, one with and one without a company,
        # it should prioritize the record with the company_id
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertEqual(content, "1.0")

        qweb_options_company_rec.field_options = "{'widget': 'monetary'}"
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertIn("$", content)

        # Test after unlinking the options record
        qweb_options_company_rec.unlink()
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertNotEqual(content, "1.0")
        self.assertNotIn("$", content)

    def test_qweb_field_option_with_uom(self):
        values = {"report_type": "pdf"}
        self.test_record.uom_id = self.unit_uom.id
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "quantity", False, False, {}, values
        )
        self.assertEqual(content, "1.000")
        self.test_record.uom_id = self.env.ref("uom.product_uom_dozen").id
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "quantity", False, False, {}, values
        )
        self.assertEqual(content, "1.0")

    def test_domain_validation(self):
        """Test that invalid domain raises validation error"""
        with self.assertRaises(ValidationError):
            self.env["qweb.field.options"].create(
                {
                    "res_model_id": self.test_model.id,
                    "field_id": self.value_field.id,
                    "domain": "invalid domain",
                    "digits": 2,
                }
            )

    def test_qweb_field_option_with_domain(self):
        values = {"report_type": "pdf"}
        jpy_currency = self.env.ref("base.JPY")
        jpy_currency.active = True
        self.qweb_options_rec.digits = 2
        self.env["qweb.field.options"].create(
            {
                "res_model_id": self.test_model.id,
                "field_id": self.value_field.id,
                "domain": f"[('currency_id', '=', {jpy_currency.id})]",
                "digits": 0,
            }
        )
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertEqual(content, "1.00")
        # Test with JPY: domain matches, uses JPY-specific option (0 digits)
        self.test_record.currency_id = jpy_currency.id
        _, content, _ = self.IrQweb._get_field(
            self.test_record, "value", False, False, {}, values
        )
        self.assertEqual(content, "1")
