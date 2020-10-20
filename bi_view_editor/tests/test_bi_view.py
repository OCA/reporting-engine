# Copyright 2017-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

import odoo
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from ..hooks import uninstall_hook


class TestBiViewEditor(TransactionCase):
    def setUp(self):
        def _get_models(model_name_list):
            return (
                self.env["ir.model"].search([("model", "=", name)])
                for name in model_name_list
            )

        def _get_fields(model_field_list):
            return (
                self.env["ir.model.fields"].search(
                    [("model", "=", model_field[0]), ("name", "=", model_field[1])],
                    limit=1,
                )
                for model_field in model_field_list
            )

        def get_new_field(self):
            return {
                "model_id": self.partner_model.id,
                "name": self.partner_field_name,
                "id": self.partner_field.id,
                "model": self.partner_model_name,
                "type": self.partner_field.ttype,
                "model_name": self.partner_model.name,
                "description": self.partner_field.field_description,
            }

        super().setUp()
        self.partner_model_name = "res.partner"
        self.partner_field_name = "name"
        self.partner_company_field_name = "company_id"
        self.company_model_name = "res.company"
        self.company_field_name = "name"

        self.bi_view1 = None

        self.partner_model, self.company_model = _get_models(
            [self.partner_model_name, self.company_model_name]
        )

        (
            self.partner_field,
            self.partner_company_field,
            self.company_field,
        ) = _get_fields(
            [
                (self.partner_model_name, self.partner_field_name),
                (self.partner_model_name, self.partner_company_field_name),
                (self.company_model_name, self.company_field_name),
            ]
        )

        self.data = [
            {
                "model_id": self.partner_model.id,
                "model_name": self.partner_model.name,
                "model": self.partner_model_name,
                "type": self.partner_field.ttype,
                "id": self.partner_field.id,
                "description": self.partner_field.field_description,
                "table_alias": "t0",
                "row": 0,
                "column": 1,
                "list": 1,
                "measure": 0,
            },
            {
                "model_id": self.partner_model.id,
                "table_alias": "t0",
                "relation": self.company_model_name,
                "model": self.partner_model_name,
                "model_name": self.partner_model.name,
                "type": self.partner_company_field.ttype,
                "id": self.partner_company_field.id,
                "join_node": "t1",
                "description": self.partner_company_field.field_description,
                "row": 0,
                "column": 0,
                "list": 1,
                "measure": 0,
            },
            {
                "model_id": self.company_model.id,
                "model_name": self.company_model.name,
                "model": self.company_model_name,
                "type": self.company_field.ttype,
                "id": self.company_field.id,
                "description": self.company_field.field_description,
                "table_alias": "t1",
                "row": 1,
                "column": 0,
                "list": 0,
                "measure": 0,
            },
        ]
        self.bi_view1_vals = {"state": "draft", "data": json.dumps(self.data)}

        self.new_field = get_new_field(self)

    def test_01_get_fields(self):
        fields = self.env["ir.model"].get_fields(self.partner_model.id)
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

    def test_02_get_join_nodes(self):
        field_res_users = self.env["ir.model.fields"].search(
            [("name", "=", "login"), ("model", "=", "res.users")], limit=1
        )
        field_data = [
            {
                "model_id": field_res_users.model_id.id,
                "name": "login",
                "column": False,
                "table_alias": "t0",
                "measure": False,
                "id": field_res_users.id,
                "model": "res.users",
                "row": False,
                "type": "char",
                "model_name": "Users",
                "description": "Login",
            }
        ]
        new_field = self.new_field
        nodes = self.env["ir.model"].get_join_nodes(field_data, new_field)
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0)

    def test_03_get_join_nodes(self):
        new_field = self.new_field
        nodes = self.env["ir.model"].get_join_nodes([], new_field)
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 0)

    def test_04_get_related_models(self):
        all_models = self.env["ir.model"].get_models()
        self.assertIsInstance(all_models, list)
        self.assertGreater(len(all_models), 0)

        related_models = self.env["ir.model"].get_models(
            {"t0": self.partner_model.id, "t1": self.company_model.id}
        )
        self.assertIsInstance(related_models, list)
        self.assertGreater(len(related_models), 0)

    def test_05_create_copy_view(self):
        vals = self.bi_view1_vals
        vals.update({"name": "Test View1"})

        # create
        bi_view1 = self.env["bve.view"].create(vals)
        self.assertIsNotNone(bi_view1)
        self.assertEqual(len(bi_view1), 1)
        self.assertEqual(bi_view1.state, "draft")

        # copy
        bi_view2 = bi_view1.copy()
        self.assertEqual(bi_view2.name, "Test View1 (copy)")

    def test_06_create_group_bve_object(self):
        vals = self.bi_view1_vals
        employees_group = self.env.ref("base.group_user")
        vals.update({"name": "Test View2", "group_ids": [(6, 0, [employees_group.id])]})

        bi_view2 = self.env["bve.view"].create(vals)
        self.assertEqual(len(bi_view2.user_ids), len(employees_group.users))

    def test_07_check_empty_data(self):
        vals = {"name": "Test View Empty", "state": "draft", "data": ""}
        bi_view4 = self.env["bve.view"].create(vals)
        self.assertEqual(len(bi_view4), 1)
        self.assertTrue(bi_view4.er_diagram_image)

        # create sql view
        with self.assertRaises(ValidationError):
            bi_view4.action_create()

    def test_08_get_models(self):
        models = self.env["ir.model"].get_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    @odoo.tests.tagged("post_install", "-at_install")
    def test_09_create_open_bve_object(self):
        vals = self.bi_view1_vals
        employees_group = self.env.ref("base.group_user")
        vals.update({"name": "Test View4", "group_ids": [(6, 0, [employees_group.id])]})
        bi_view = self.env["bve.view"].create(vals)
        self.assertEqual(len(bi_view), 1)
        self.assertEqual(len(bi_view.line_ids), 3)
        self.assertTrue(bi_view.er_diagram_image)

        # check lines
        line1 = bi_view.line_ids[0]
        line2 = bi_view.line_ids[1]
        line3 = bi_view.line_ids[2]
        self.assertTrue(line1.in_list)
        self.assertTrue(line2.in_list)
        self.assertFalse(line3.in_list)
        self.assertFalse(line1.row)
        self.assertTrue(line1.column)
        self.assertFalse(line1.measure)
        self.assertFalse(line2.row)
        self.assertFalse(line2.column)
        self.assertFalse(line2.measure)
        self.assertTrue(line3.row)
        self.assertFalse(line3.column)
        self.assertFalse(line3.measure)

        # create bve object
        bi_view.action_create()
        model = self.env["ir.model"].search(
            [("model", "=", "x_bve.testview4"), ("name", "=", "Test View4")]
        )
        self.assertEqual(len(model), 1)

        # open view
        open_action = bi_view.open_view()
        self.assertEqual(isinstance(open_action, dict), True)
        self.assertEqual(bi_view.state, "created")

        # try to remove view
        with self.assertRaises(UserError):
            bi_view.unlink()

        # reset to draft
        bi_view.action_reset()
        self.assertEqual(bi_view.state, "draft")

        # remove view
        bi_view.unlink()

    @odoo.tests.tagged("post_install", "-at_install")
    def test_10_create_open_bve_object_apostrophe(self):
        vals = self.bi_view1_vals
        vals.update({"name": "Test View5"})
        data_list = list()
        for r in json.loads(vals["data"]):
            r["model_name"] = "model'name"
            data_list.append(r)
        new_format_data = json.dumps(data_list)
        vals.update({"data": new_format_data})
        bi_view = self.env["bve.view"].create(vals)
        self.assertEqual(len(bi_view), 1)
        # create bve object
        bi_view.action_create()

    def test_11_clean_nodes(self):
        data_dict1 = {
            "sequence": 1,
            "model_id": 74,
            "id": 858,
            "name": "name",
            "model_name": "Contact",
            "model": "res.partner",
            "type": "char",
            "table_alias": "t74",
            "description": "Name",
            "row": False,
            "column": False,
            "measure": False,
            "list": True,
        }
        data_dict2 = {
            "sequence": 2,
            "model_id": 74,
            "id": 896,
            "name": "company_id",
            "model_name": "Contact",
            "model": "res.partner",
            "type": "many2one",
            "table_alias": "t74",
            "description": "Company",
            "row": False,
            "column": False,
            "measure": False,
            "list": True,
            "join_node": "t83",
            "relation": "res.company",
            "join_left": False,
        }

        old_data = json.dumps([data_dict1, data_dict2])
        new_data = self.env["bve.view"].get_clean_list(old_data)
        new_data_dict = json.loads(new_data)
        self.assertEqual(len(new_data_dict), 1)
        for key in data_dict1.keys():
            self.assertEqual(new_data_dict[0][key], data_dict1[key])

    def test_12_check_groups(self):
        vals = self.bi_view1_vals
        group_system = self.env.ref("base.group_system")
        vals.update({"name": "Test View1", "group_ids": [(6, 0, [group_system.id])]})
        bi_view1 = self.env["bve.view"].create(vals)
        with self.assertRaises(UserError):
            bi_view1.action_create()

    def test_13_check_lines_missing_model(self):
        vals = self.bi_view1_vals
        group_user = self.env.ref("base.group_user")
        vals.update({"name": "Test View1", "group_ids": [(6, 0, [group_user.id])]})
        bi_view1 = self.env["bve.view"].create(vals)
        for line in bi_view1.line_ids:
            self.assertTrue(line.model_id)
            self.assertTrue(line.model_name)
        self.env.cr.execute("UPDATE bve_view_line SET model_id = null")
        bi_view1.invalidate_cache()
        for line in bi_view1.line_ids:
            self.assertFalse(line.model_id)
            self.assertTrue(line.model_name)
        with self.assertRaises(ValidationError):
            bi_view1.action_create()

    def test_14_check_lines_missing_fieldl(self):
        vals = self.bi_view1_vals
        group_user = self.env.ref("base.group_user")
        vals.update({"name": "Test View1", "group_ids": [(6, 0, [group_user.id])]})
        bi_view1 = self.env["bve.view"].create(vals)
        for line in bi_view1.line_ids:
            self.assertTrue(line.field_id)
            self.assertTrue(line.field_name)
        self.env.cr.execute("UPDATE bve_view_line SET field_id = null")
        bi_view1.invalidate_cache()
        for line in bi_view1.line_ids:
            self.assertFalse(line.field_id)
            self.assertTrue(line.field_name)
        with self.assertRaises(ValidationError):
            bi_view1.action_create()

    def test_15_create_lines(self):
        vals = self.bi_view1_vals
        vals.update({"name": "Test View1"})
        bi_view1 = self.env["bve.view"].create(vals)
        bi_view1._compute_serialized_data()
        data = json.loads(bi_view1.data)
        self.assertTrue(data)
        self.assertTrue(isinstance(data, list))

    def test_17_uninstall_hook(self):
        uninstall_hook(self.cr, self.env)

    def test_18_action_translations(self):
        self.env["res.lang"]._activate_lang("it_IT")
        vals = self.bi_view1_vals
        vals.update({"name": "Test View1"})
        bi_view1 = self.env["bve.view"].create(vals)
        res = bi_view1.action_translations()
        self.assertFalse(res)

        bi_view1.action_create()
        res = bi_view1.action_translations()
        self.assertTrue(res)

    @odoo.tests.tagged("post_install", "-at_install")
    def test_19_field_selection(self):
        field = self.env["ir.model.fields"].search(
            [
                ("model", "=", self.company_model_name),
                ("name", "=", "base_onboarding_company_state"),
            ],
            limit=1,
        )
        selection_data = [
            {
                "model_id": self.company_model.id,
                "model_name": self.company_model.name,
                "model": self.company_model_name,
                "type": field.ttype,
                "id": field.id,
                "description": "State of the onboarding company step",
                "table_alias": "t1",
                "row": 0,
                "column": 0,
                "list": 1,
                "measure": 0,
            }
        ]
        vals = {"state": "draft", "data": json.dumps(self.data + selection_data)}

        vals.update({"name": "Test View6"})
        bi_view1 = self.env["bve.view"].create(vals)
        bi_view1.action_create()
        self.assertEqual(len(bi_view1.line_ids), 4)

    @mute_logger("odoo.sql_db")
    def test_20_broken_view(self):
        """
        Create a broken query, a nice UserError should be raised.
        odoo.sql_db logger is muted to avoid the
        ERROR: bad_query line in the logs.
        """
        vals = self.bi_view1_vals
        vals.update({"name": "Test View broken", "over_condition": "bad SQL code"})
        bi_view = self.env["bve.view"].create(vals)
        with self.assertRaises(UserError) as ue:
            bi_view.action_create()

        self.assertEqual(bi_view.state, "draft")
        self.assertIn(bi_view.over_condition, str(ue.exception))
        # remove view
        bi_view.unlink()
