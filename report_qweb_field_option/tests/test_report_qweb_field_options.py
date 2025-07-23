# Copyright 2024 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestQwebFieldOptions(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from .test_models import TestQwebFieldModel

        cls.loader.update_registry((TestQwebFieldModel,))
        cls.test_model = cls.env.ref(
            "report_qweb_field_option.model_test_qweb_field_options"
        )
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

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        return super().tearDownClass()

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
