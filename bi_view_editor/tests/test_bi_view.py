# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests.common import TransactionCase, at_install, post_install
from odoo.exceptions import Warning as UserError


class TestBiViewEditor(TransactionCase):

    def setUp(self):

        def _get_models(model_name_list):
            Model = self.env['ir.model']
            return (Model.search(
                [('model', '=', name)]) for name in model_name_list)

        def _get_fields(model_field_list):
            ModelFields = self.env['ir.model.fields']
            return (ModelFields.search(
                [('model', '=', model_field[0]),
                 ('name', '=', model_field[1])],
                limit=1) for model_field in model_field_list)

        def get_new_field(self):
            new_field = {
                'model_id': self.partner_model.id,
                'name': self.partner_field_name,
                'custom': False,
                'id': self.partner_field.id,
                'model': self.partner_model_name,
                'type': self.partner_field.ttype,
                'model_name': self.partner_model.name,
                'description': self.partner_field.field_description
            }
            return new_field

        super(TestBiViewEditor, self).setUp()
        self.partner_model_name = 'res.partner'
        self.partner_field_name = 'name'
        self.partner_company_field_name = 'company_id'
        self.company_model_name = 'res.company'
        self.company_field_name = 'name'

        self.bi_view1 = None

        self.partner_model, self.company_model = _get_models(
            [self.partner_model_name, self.company_model_name])

        (self.partner_field,
         self.partner_company_field,
         self.company_field) = _get_fields([
             (self.partner_model_name, self.partner_field_name),
             (self.partner_model_name, self.partner_company_field_name),
             (self.company_model_name, self.company_field_name)])

        data = [
            {'model_id': self.partner_model.id,
             'name': self.partner_field_name,
             'model_name': self.partner_model.name,
             'model': self.partner_model_name,
             'custom': 0,
             'type': self.partner_field.ttype,
             'id': self.partner_field.id,
             'description': self.partner_field.field_description,
             'table_alias': 't0',
             'row': 0,
             'column': 1,
             'list': 1,
             'measure': 0
             },
            {'model_id': self.partner_model.id,
             'name': self.partner_company_field_name,
             'table_alias': 't0',
             'custom': 0,
             'relation': self.company_model_name,
             'model': self.partner_model_name,
             'model_name': self.partner_model.name,
             'type': self.partner_company_field.ttype,
             'id': self.partner_company_field.id,
             'join_node': 't1',
             'description': self.partner_company_field.field_description,
             'row': 0,
             'column': 0,
             'list': 1,
             'measure': 0
             },
            {'model_id': self.company_model.id,
             'name': 'name_1',
             'model_name': self.company_model.name,
             'model': self.company_model_name,
             'custom': 0,
             'type': self.company_field.ttype,
             'id': self.company_field.id,
             'description': self.company_field.field_description,
             'table_alias': 't1',
             'row': 1,
             'column': 0,
             'list': 0,
             'measure': 0
             }
        ]
        format_data = self.env['bve.view']._get_format_data(str(data))

        self.bi_view1_vals = {
            'state': 'draft',
            'data': format_data
        }

        self.new_field = get_new_field(self)

    def test_01_get_fields(self):
        Model = self.env['ir.model']
        fields = Model.get_fields(self.partner_model.id)
        self.assertIsInstance(fields, list)
        self.assertGreater(len(fields), 0)

    def test_02_get_join_nodes(self):
        Fields = self.env['ir.model.fields']
        field_res_users = Fields.search([
            ('name', '=', 'login'),
            ('model', '=', 'res.users')
        ], limit=1)
        field_data = [{
            'model_id': field_res_users.model_id.id,
            'name': 'login',
            'column': False,
            'table_alias': 't0',
            'custom': False,
            'measure': False,
            'id': field_res_users.id,
            'model': 'res.users',
            'row': False,
            'type': 'char',
            'model_name': 'Users',
            'description': 'Login'
        }]
        new_field = self.new_field
        Model = self.env['ir.model']
        nodes = Model.get_join_nodes(field_data, new_field)
        self.assertIsInstance(nodes, list)
        self.assertGreater(len(nodes), 0)

    def test_03_get_join_nodes(self):
        new_field = self.new_field
        Model = self.env['ir.model']
        nodes = Model.get_join_nodes([], new_field)
        self.assertIsInstance(nodes, list)
        self.assertEqual(len(nodes), 0)

    def test_04_get_related_models(self):
        Model = self.env['ir.model']
        related_models = Model.get_related_models({
            't0': self.partner_model.id,
            't1': self.company_model.id
        })
        self.assertIsInstance(related_models, list)
        self.assertGreater(len(related_models), 0)

    def test_05_create_copy_view(self):
        vals = self.bi_view1_vals
        vals.update({'name': 'Test View1'})

        # create
        bi_view1 = self.env['bve.view'].create(vals)
        self.assertIsNotNone(bi_view1)
        self.assertEqual(len(bi_view1), 1)
        self.assertEqual(bi_view1.state, 'draft')

        # copy
        bi_view2 = bi_view1.copy()
        self.assertEqual(bi_view2.name, 'Test View1 (copy)')

    def test_06_create_group_bve_object(self):
        vals = self.bi_view1_vals
        employees_group = self.env.ref('base.group_user')
        vals.update({
            'name': 'Test View2',
            'group_ids': [(6, 0, [employees_group.id])],
        })

        bi_view2 = self.env['bve.view'].create(vals)
        self.assertEqual(len(bi_view2.user_ids), len(employees_group.users))

    def test_07_check_empty_data(self):
        vals = {
            'name': 'Test View Empty',
            'state': 'draft',
            'data': ''
        }
        bi_view4 = self.env['bve.view'].create(vals)
        self.assertEqual(len(bi_view4), 1)

        # create sql view
        with self.assertRaises(UserError):
            bi_view4.action_create()

    def test_08_get_models(self):
        Model = self.env['ir.model']
        models = Model.get_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)

    @at_install(False)
    @post_install(True)
    def test_09_create_open_bve_object(self):
        vals = self.bi_view1_vals
        employees_group = self.env.ref('base.group_user')
        vals.update({
            'name': 'Test View4',
            'group_ids': [(6, 0, [employees_group.id])],
        })
        bi_view = self.env['bve.view'].create(vals)
        self.assertEqual(len(bi_view), 1)

        # create bve object
        bi_view.action_create()
        model = self.env['ir.model'].search([
            ('model', '=', 'x_bve.testview4'),
            ('name', '=', 'Test View4')
        ])
        self.assertEqual(len(model), 1)

        # open view
        open_action = bi_view.open_view()
        self.assertEqual(isinstance(open_action, dict), True)

        # try to remove view
        with self.assertRaises(UserError):
            bi_view.unlink()
