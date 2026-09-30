# Copyright 2026 Quartile (https://www.quartile.co)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import lxml.html
from markupsafe import Markup

from odoo import Command
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tools import mute_logger

from odoo.addons.base.tests.common import BaseCommon

LOGGER = "odoo.addons.report_positioned_image.models.report_positioned_image"


# 'res.partner' is only complete once every module extending it is loaded: at
# install time it still lacks e.g. account's required columns.
@tagged("post_install", "-at_install")
class TestReportPositionedImage(BaseCommon):
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

    def _make_header(self, count):
        """Mimic what _prepare_html renders: one child per body."""
        children = "".join(
            f'<div class="header">HEADER-{index}</div>' for index in range(count)
        )
        return Markup(
            "<!DOCTYPE html><html><body>"
            f'<div id="minimal_layout_report_headers">{children}</div>'
            "</body></html>"
        )

    def _setup_condition(self):
        """Make image_a conditional on companies, and link it to the report."""
        self.image_a.domain = "[('is_company', '=', True)]"
        self.report.write(
            {
                "include_company_images": False,
                "report_positioned_image_ids": [Command.set([self.image_a.id])],
            }
        )
        matching = self.env["res.partner"].create(
            {"name": "Matching Co", "is_company": True}
        )
        other = self.env["res.partner"].create(
            {"name": "Skipped Contact", "is_company": False}
        )
        return self.report.with_company(self.company_a), matching, other

    def test_condition_validated_against_the_linked_reports(self):
        """The condition is checked against the model of every report using it."""
        self._setup_condition()
        for invalid in ("[('no_such_field', '=', True)]", "not a domain"):
            with self.assertRaises(ValidationError):
                self.image_a.domain = invalid
        # Linking the image to a report whose model cannot evaluate it is refused
        # too, so the check cannot be bypassed from the report side.
        country_report = self.env["ir.actions.report"].create(
            {
                "name": "Country Report",
                "model": "res.country",
                "report_type": "qweb-pdf",
                "report_name": "test_country_report",
            }
        )
        with self.assertRaises(ValidationError):
            country_report.report_positioned_image_ids = [
                Command.set([self.image_a.id])
            ]

    def test_one_condition_guards_reports_on_several_models(self):
        """The condition takes its model from the report, so it is not bound to one."""
        report, _matching, _other = self._setup_condition()
        user_report = self.env["ir.actions.report"].create(
            {
                "name": "User Report",
                "model": "res.users",
                "report_type": "qweb-pdf",
                "report_name": "test_user_report",
                "report_positioned_image_ids": [Command.set([self.image_a.id])],
            }
        )
        for conditional in (report, user_report.with_company(self.company_a)):
            self.assertFalse(conditional._get_positioned_image_configs())
            self.assertEqual(
                conditional._get_conditional_positioned_images(), self.image_a
            )

    @mute_logger(LOGGER)
    def test_condition_unusable_on_the_printed_model_matches_nothing(self):
        """An image is skipped, not printed unguarded, where it does not apply."""
        self._setup_condition()
        countries = self.env["res.country"].search([], limit=2)
        self.assertFalse(
            self.image_a._get_condition_matched_ids(
                self.env["res.country"], countries.ids
            )
        )

    def test_inject_conditional_images_into_header(self):
        """The image lands in the matching record's header child, and only there."""
        report, matching, other = self._setup_condition()
        self.image_a.first_page_only = True
        res_ids = [matching.id, other.id]
        result = report._inject_conditional_images_into_header(
            self._make_header(2),
            res_ids,
            self.image_a,
            report._get_condition_matches(res_ids, self.image_a),
        )
        headers = lxml.html.fromstring(result).xpath(
            "//*[@id='minimal_layout_report_headers']"
        )[0]
        self.assertEqual(len(headers), 2, "the per-record children must be preserved")
        self.assertTrue(headers[0].xpath(".//img"))
        self.assertFalse(headers[1].xpath(".//img"))
        # subst() runs in the header, so 'first_page_only' still applies.
        self.assertIn("first-page", str(result))
        self.assertIn("<!DOCTYPE html>", str(result))

    def test_inject_conditional_images_falls_back_to_bodies(self):
        """Without one header per record, the image goes into the bodies instead."""
        report, matching, _other = self._setup_condition()
        self.image_a.first_page_only = True
        # One body has no identifiable record, and a third has no res_id at all.
        bodies = [Markup(f"<html><body>{name}</body></html>") for name in "abc"]
        res_ids = [None, matching.id]
        matched_ids = report._get_condition_matches(res_ids, self.image_a)
        self.assertIsNone(
            report._inject_conditional_images_into_header(
                self._make_header(1), res_ids, self.image_a, matched_ids
            )
        )
        new_bodies = report._inject_conditional_images_into_bodies(
            bodies, res_ids, self.image_a, matched_ids
        )
        self.assertEqual(len(new_bodies), len(bodies))
        self.assertNotIn("<img", str(new_bodies[0]))
        self.assertIn('<img src="data:image/', str(new_bodies[1]))
        self.assertNotIn("<img", str(new_bodies[2]))
        # 'first_page_only' is inert in a body: subst() never runs there.
        self.assertNotIn("first-page", str(new_bodies[1]))
