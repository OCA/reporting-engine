from odoo_test_helper import FakeModelLoader

from odoo.exceptions import ValidationError

from odoo.addons.base.tests.common import BaseCommon


class TestReportPrintedFlag(BaseCommon):
    """Test suite for report_printed_flag module.
    This test class validates the full behavior of the module including:
    - Printed flag assignment
    - Log creation
    - Configuration filtering
    - Multi-record handling
    - Multi-company isolation
    - Safe behavior on models without 'printed' field
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # ---------------------------
        # LOAD TEST MODEL (OCA style)
        # ---------------------------
        cls.loader = FakeModelLoader(cls.env, cls.__module__)
        cls.loader.backup_registry()
        from . import test_models

        cls.loader.update_registry(
            (
                test_models.TestPrintedModel,
                test_models.TestPrintedNoNameModel,
            )
        )
        cls.model_name = "test.printed.model"
        cls.model = cls.env["ir.model"]._get(cls.model_name)
        # ---------------------------
        # DATA
        # ---------------------------
        cls.company = cls.env.company
        cls.record = cls.env[cls.model_name].create(
            {
                "name": "Test Record",
                "company_id": cls.company.id,
            }
        )
        # ---------------------------
        # QWEB TEMPLATE (MANDATORY)
        # ---------------------------
        cls.env["ir.ui.view"].create(
            {
                "name": "test_report_template",
                "type": "qweb",
                "key": "report_printed_flag.test_report_template",
                "arch": """
                <t t-name="report_printed_flag.test_report_template">
                    <t t-foreach="docs" t-as="o">
                        <div>
                            <span t-esc="o.id"/>
                        </div>
                    </t>
                </t>
            """,
            }
        )
        # ---------------------------
        # REPORT
        # ---------------------------
        cls.report = cls.env["ir.actions.report"].create(
            {
                "name": "Test Report",
                "model": cls.model_name,
                "report_type": "qweb-pdf",
                "report_name": "report_printed_flag.test_report_template",
            }
        )
        # ---------------------------
        # CONFIG
        # ---------------------------
        cls.config = cls.env["report.printed.config"].create(
            {
                "name": "Test Config",
                "model_id": cls.model.id,
                "company_id": cls.company.id,
                "report_printed_log_active": True,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "report_id": cls.report.id,
                        },
                    )
                ],
            }
        )

    @classmethod
    def tearDownClass(cls):
        cls.loader.restore_registry()
        super().tearDownClass()

    # ---------------------------
    # CORE FUNCTIONALITY
    # ---------------------------
    def test_printed_flag(self):
        """Printing a configured report should set the 'printed' flag."""
        self.assertFalse(self.record.printed)
        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )
        self.record.invalidate_recordset()
        self.assertTrue(self.record.printed)

    def test_log_created(self):
        """Printing should create a log entry."""
        self.env["report.printed.log"].search([]).unlink()
        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )
        logs = self.env["report.printed.log"].search(
            [
                ("res_model", "=", self.model_name),
                ("res_id", "=", self.record.id),
            ]
        )
        self.assertTrue(logs)

    def test_log_values(self):
        """Log should contain correct metadata."""
        self.env["report.printed.log"].search([]).unlink()
        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )
        log = self.env["report.printed.log"].search([], limit=1)
        self.assertEqual(log.name, self.record.name)
        self.assertEqual(log.res_model, self.model_name)
        self.assertEqual(log.res_id, self.record.id)
        self.assertEqual(log.report_id, self.report)
        self.assertEqual(log.company_id, self.company)
        self.assertEqual(log.user_id, self.env.user)

    # ---------------------------
    # CONFIGURATION BEHAVIOR
    # ---------------------------
    def test_report_not_configured(self):
        """Reports not present in config should not affect records."""
        other_report = self.env["ir.actions.report"].create(
            {
                "name": "Other Report",
                "model": self.model_name,
                "report_type": "qweb-pdf",
                "report_name": "report_printed_flag.test_report_template",
            }
        )
        self.record.write({"printed": False})
        other_report._render_qweb_pdf(
            other_report.report_name,
            self.record.ids,
        )
        self.record.invalidate_recordset()
        self.assertFalse(self.record.printed)

    # ---------------------------
    # BATCH PROCESSING
    # ---------------------------
    def test_multiple_records(self):
        """Printing multiple records should mark all of them."""
        rec2 = self.env[self.model_name].create(
            {
                "name": "Test Record 2",
                "company_id": self.company.id,
            }
        )
        self.report._render_qweb_pdf(
            self.report.report_name,
            (self.record | rec2).ids,
        )
        self.record.invalidate_recordset()
        rec2.invalidate_recordset()
        self.assertTrue(self.record.printed)
        self.assertTrue(rec2.printed)

    def test_multiple_prints_create_multiple_logs(self):
        """Each print should generate a log entry."""
        self.env["report.printed.log"].search([]).unlink()
        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )
        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )
        logs = self.env["report.printed.log"].search(
            [
                ("res_id", "=", self.record.id),
            ]
        )
        self.assertEqual(len(logs), 2)

    # ---------------------------
    # ROBUSTNESS
    # ---------------------------
    def test_model_without_printed_field(self):
        """System must not crash if model lacks 'printed' field."""
        partner = self.env["res.partner"].create(
            {
                "name": "No Printed Field",
            }
        )
        report = self.env["ir.actions.report"].create(
            {
                "name": "Partner Report",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "report_printed_flag.test_report_template",
            }
        )
        # Should not raise
        report._render_qweb_pdf(
            report.report_name,
            partner.ids,
        )
        self.assertTrue(True)

    def test_model_without_name_field(self):
        """System should fallback to display_name if 'name' field is missing."""
        model_name = "test.printed.noname.model"
        record = self.env[model_name].create(
            {
                "value": "No Name",
                "company_id": self.company.id,
            }
        )
        report = self.env["ir.actions.report"].create(
            {
                "name": "NoName Report",
                "model": model_name,
                "report_type": "qweb-pdf",
                "report_name": "report_printed_flag.test_report_template",
            }
        )
        self.env["report.printed.config"].create(
            {
                "name": "NoName Config",
                "model_id": self.env["ir.model"]._get(model_name).id,
                "company_id": self.company.id,
                "report_printed_log_active": True,
                "line_ids": [
                    (
                        0,
                        0,
                        {
                            "report_id": report.id,
                        },
                    )
                ],
            }
        )
        report._render_qweb_pdf(
            report.report_name,
            record.ids,
        )
        log = self.env["report.printed.log"].search(
            [
                ("res_model", "=", model_name),
                ("res_id", "=", record.id),
            ],
            limit=1,
        )
        self.assertTrue(log)
        self.assertTrue(log.name)  # should exist (display_name fallback)

    # ---------------------------
    # CONFIG CONSTRAINTS
    # ---------------------------
    def test_config_rejects_model_without_printed_field(self):
        """Configuration must reject models without a printed field."""
        partner_model = self.env["ir.model"]._get("res.partner")
        with self.assertRaises(ValidationError):
            self.env["report.printed.config"].create(
                {
                    "name": "Invalid Partner Config",
                    "model_id": partner_model.id,
                    "company_id": self.company.id,
                }
            )

    def test_config_rejects_report_from_different_model(self):
        """Configured reports must belong to the selected model."""
        partner_report = self.env["ir.actions.report"].create(
            {
                "name": "Partner Report Invalid",
                "model": "res.partner",
                "report_type": "qweb-pdf",
                "report_name": "report_printed_flag.test_report_template",
            }
        )

        # Reuse existing config to avoid unique(company_id, model_id) conflict.
        with self.assertRaises(ValidationError):
            self.config.write(
                {
                    "line_ids": [
                        (
                            0,
                            0,
                            {
                                "report_id": partner_report.id,
                            },
                        )
                    ],
                }
            )

    def test_config_report_names_require_logs(self):
        """Printed report names require printed logs to be enabled."""
        with self.assertRaises(ValidationError):
            self.config.write(
                {
                    "report_printed_log_active": False,
                    "report_printed_names_active": True,
                }
            )

    def test_onchange_report_names_active_enables_logs(self):
        """Enabling printed report names should auto-enable logs."""
        config = self.env["report.printed.config"].new(
            {
                "name": "Onchange Config",
                "model_id": self.model.id,
                "company_id": self.company.id,
                "report_printed_log_active": False,
                "report_printed_names_active": True,
            }
        )

        config._onchange_report_names_active()

        self.assertTrue(config.report_printed_log_active)

    def test_onchange_report_log_inactive_disables_names(self):
        """Disabling printed logs should disable printed report names."""
        config = self.env["report.printed.config"].new(
            {
                "name": "Onchange Config",
                "model_id": self.model.id,
                "company_id": self.company.id,
                "report_printed_log_active": False,
                "report_printed_names_active": True,
            }
        )

        config._onchange_report_log_active()

        self.assertFalse(config.report_printed_names_active)

    # ---------------------------
    # DOMAIN VALIDATION
    # ---------------------------
    def test_valid_domain_constraint(self):
        """Valid domain syntax should be accepted."""
        self.config.line_ids[:1].write(
            {
                "domain": "[('name', '=', 'Test Record')]",
            }
        )
        self.assertEqual(
            self.config.line_ids[:1].domain,
            "[('name', '=', 'Test Record')]",
        )

    # ---------------------------
    # DOMAIN FILTERING
    # ---------------------------
    def test_domain_filtering_skips_non_matching_record(self):
        """Domain rules should skip records that do not match."""
        self.config.line_ids[:1].domain = "[('name', '=', 'Other Name')]"
        self.record.write({"printed": False})

        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )

        self.record.invalidate_recordset()
        self.assertFalse(self.record.printed)

    def test_domain_filtering_allows_matching_record(self):
        """Domain rules should allow matching records."""
        self.config.line_ids[:1].domain = "[('name', '=', 'Test Record')]"
        self.record.write({"printed": False})

        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )

        self.record.invalidate_recordset()
        self.assertTrue(self.record.printed)

    # ---------------------------
    # EARLY RETURN / DISABLED OPTIONS
    # ---------------------------
    def test_apply_printed_flag_without_report(self):
        """Applying without report should safely return."""
        self.env["ir.actions.report"]._apply_printed_flag(
            False,
            self.record.ids,
        )
        self.assertTrue(True)

    def test_apply_printed_flag_without_res_ids(self):
        """Applying without res_ids should safely return."""
        self.env["ir.actions.report"]._apply_printed_flag(
            self.report,
            [],
        )
        self.assertTrue(True)

    def test_config_inactive_does_not_mark_printed(self):
        """Inactive configurations should not affect records."""
        self.config.active = False
        self.record.write({"printed": False})

        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )

        self.record.invalidate_recordset()
        self.assertFalse(self.record.printed)
        self.config.active = True

    def test_logs_disabled(self):
        """Logs should not be created when disabled."""
        self.config.report_printed_names_active = False
        self.config.report_printed_log_active = False
        self.env["report.printed.log"].search([]).unlink()

        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )

        logs = self.env["report.printed.log"].search(
            [
                ("res_model", "=", self.model_name),
                ("res_id", "=", self.record.id),
            ]
        )
        self.assertFalse(logs)

    # ---------------------------
    # MIXIN BEHAVIOR
    # ---------------------------
    def test_printed_report_names(self):
        """Printed report names should be computed from logs."""
        self.env["report.printed.log"].search([]).unlink()

        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )

        self.record.invalidate_recordset(["printed_report_names"])
        self.assertIn("Test Report", self.record.printed_report_names)

    def test_printed_report_names_disabled(self):
        """Printed report names should be empty when feature is disabled."""
        self.config.report_printed_names_active = False
        self.env["report.printed.log"].search([]).unlink()

        self.report._render_qweb_pdf(
            self.report.report_name,
            self.record.ids,
        )

        self.record.invalidate_recordset(["printed_report_names"])
        self.assertFalse(self.record.printed_report_names)

        self.config.report_printed_names_active = True

    def test_action_view_printed_logs(self):
        """Mixin action should open printed logs for the current record."""
        action = self.record.action_view_printed_logs()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "report.printed.log")
        self.assertEqual(action["view_mode"], "tree")
        self.assertIn(("res_model", "=", self.model_name), action["domain"])
        self.assertIn(("res_id", "=", self.record.id), action["domain"])
