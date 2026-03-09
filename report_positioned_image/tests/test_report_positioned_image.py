# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from markupsafe import Markup

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestReportPositionedImage(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_a = cls.env.ref("base.main_company")
        cls.company_b = cls.env["res.company"].create({"name": "Company B"})
        cls.report = cls.env["ir.actions.report"].create(
            {
                "name": "Test Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "test_report",
            }
        )
        # Create a simple 1x1 transparent PNG for testing (base64-encoded)
        cls.test_image = (
            b"iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhg"
            b"GAWjR9awAAAABJRU5ErkJggg=="
        )
        cls.image_a = cls.env["report.positioned.image"].create(
            {
                "name": "Company A Image",
                "image": cls.test_image,
                "pos_top": 10.0,
                "pos_left": 15.0,
                "width": 25.0,
                "height": 30.0,
                "first_page_only": False,
                "company_id": cls.company_a.id,
            }
        )
        cls.company_a.write(
            {"report_positioned_image_ids": [Command.set([cls.image_a.id])]}
        )
        cls.image_b = cls.env["report.positioned.image"].create(
            {
                "name": "Company B Image",
                "image": cls.test_image,
                "pos_top": 50.0,
                "pos_left": 60.0,
                "width": 70.0,
                "height": 80.0,
                "first_page_only": True,
                "company_id": cls.company_b.id,
            }
        )
        cls.company_b.write(
            {"report_positioned_image_ids": [Command.set([cls.image_b.id])]}
        )
        cls.global_image = cls.env["report.positioned.image"].create(
            {
                "name": "Global Image",
                "image": cls.test_image,
                "pos_top": 5.0,
                "pos_left": 5.0,
                "width": 10.0,
                "height": 10.0,
                "company_id": False,
            }
        )

    def test_company_images_respects_company_context(self):
        self.report.include_company_images = True
        configs = self.report.with_company(
            self.company_a
        )._get_positioned_image_configs()
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0]["pos_top"], 10.0)
        self.assertEqual(configs[0]["pos_left"], 15.0)
        self.assertFalse(configs[0]["first_page_only"])
        configs = self.report.with_company(
            self.company_b
        )._get_positioned_image_configs()
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0]["pos_top"], 50.0)
        self.assertEqual(configs[0]["pos_left"], 60.0)
        self.assertTrue(configs[0]["first_page_only"])

    def test_report_images_filter_by_company(self):
        self.report.write(
            {
                "include_company_images": False,
                "report_positioned_image_ids": [
                    Command.set([self.image_a.id, self.image_b.id])
                ],
            }
        )
        configs = self.report.with_company(
            self.company_a
        )._get_positioned_image_configs()
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0]["pos_top"], 10.0)
        configs = self.report.with_company(
            self.company_b
        )._get_positioned_image_configs()
        self.assertEqual(len(configs), 1)
        self.assertEqual(configs[0]["pos_top"], 50.0)

    def test_combined_company_and_report_images(self):
        custom_image = self.env["report.positioned.image"].create(
            {
                "name": "Custom Report Image",
                "image": self.test_image,
                "pos_top": 100.0,
                "pos_left": 110.0,
                "width": 120.0,
                "height": 130.0,
                "first_page_only": False,
                "company_id": self.company_a.id,
            }
        )
        self.report.write(
            {
                "include_company_images": True,
                "report_positioned_image_ids": [Command.set([custom_image.id])],
            }
        )
        configs = self.report.with_company(
            self.company_a
        )._get_positioned_image_configs()
        self.assertEqual(len(configs), 2)
        self.assertEqual(configs[0]["pos_top"], 100.0)
        self.assertEqual(configs[1]["pos_top"], 10.0)

    def test_validation_negative_dimensions(self):
        with self.assertRaises(ValidationError):
            self.env["report.positioned.image"].create(
                {
                    "name": "Invalid Image",
                    "image": self.test_image,
                    "width": -10.0,
                    "company_id": self.company_a.id,
                }
            )
        with self.assertRaises(ValidationError):
            self.image_a.write({"height": -5.0})

    def test_build_image_html_positioning(self):
        images = [
            {
                "image": self.test_image,
                "pos_top": 5,
                "pos_left": 10,
                "width": 20,
                "height": 15,
            }
        ]
        html = self.report._build_image_html(images)
        html_str = str(html)
        self.assertIn("position: fixed", html_str)
        self.assertIn("top: 5mm", html_str)
        self.assertIn("left: 10mm", html_str)
        self.assertIn("width: 20mm", html_str)
        self.assertIn("height: 15mm", html_str)
        self.assertIn('<img src="data:image/', html_str)

    def test_build_image_html_with_first_page_class(self):
        images = [
            {
                "image": self.test_image,
                "pos_top": 5,
                "pos_left": 10,
                "width": 20,
                "height": 15,
                "first_page_only": True,
            }
        ]
        html = self.report._build_image_html(images)
        html_str = str(html)
        self.assertIn('class="first-page"', html_str)
        self.assertIn("position: fixed", html_str)
        self.assertIn("top: 5mm", html_str)

    def test_build_image_html_without_first_page_class(self):
        images = [
            {
                "image": self.test_image,
                "pos_top": 5,
                "pos_left": 10,
                "width": 20,
                "height": 15,
                "first_page_only": False,
            }
        ]
        html = self.report._build_image_html(images)
        html_str = str(html)
        self.assertNotIn("class=", html_str)
        self.assertIn("position: fixed", html_str)
        self.assertIn("top: 5mm", html_str)

    def test_inject_images_uses_first_page_class(self):
        images = [
            {
                "image": self.test_image,
                "pos_top": 5,
                "pos_left": 10,
                "width": 20,
                "height": 15,
                "first_page_only": True,
            }
        ]
        header = Markup("<html><body></body></html>")
        result = self.report._inject_images_into_header(header, images)
        result_str = str(result)
        # Should contain the first-page class
        self.assertIn('class="first-page"', result_str)

    def test_global_images_appear_for_all_companies(self):
        self.report.write(
            {
                "report_positioned_image_ids": [
                    Command.set([self.global_image.id, self.image_a.id])
                ]
            }
        )
        configs_a = self.report.with_company(
            self.company_a
        )._get_positioned_image_configs()
        self.assertEqual(len(configs_a), 2)
        # Company B sees: global only (not image_a)
        configs_b = self.report.with_company(
            self.company_b
        )._get_positioned_image_configs()
        self.assertEqual(len(configs_b), 1)

    def test_company_id_onchange_with_context(self):
        image = (
            self.env["report.positioned.image"]
            .with_context(default_company_id=self.company_a.id)
            .new(
                {
                    "name": "Test Image",
                    "image": self.test_image,
                    "width": 10.0,
                    "height": 10.0,
                    "company_id": self.company_a.id,
                }
            )
        )
        image.company_id = self.company_b
        result = image._onchange_company_id()
        self.assertIsNotNone(result)
        self.assertIn("warning", result)
        self.assertEqual(image.company_id, self.company_a)
        image.company_id = self.company_a
        result = image._onchange_company_id()
        self.assertIsNone(result)
        self.assertEqual(image.company_id, self.company_a)
        image.company_id = False
        result = image._onchange_company_id()
        self.assertIsNone(result)
        self.assertFalse(image.company_id)
        image_no_context = self.env["report.positioned.image"].new(
            {
                "name": "Free Image",
                "image": self.test_image,
                "width": 10.0,
                "height": 10.0,
                "company_id": self.company_b.id,
            }
        )
        result = image_no_context._onchange_company_id()
        self.assertIsNone(result)
        self.assertEqual(image_no_context.company_id, self.company_b)
