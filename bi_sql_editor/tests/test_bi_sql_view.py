# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase, at_install, post_install
from openerp.exceptions import Warning as UserError


@at_install(False)
@post_install(True)
class TestBiSqlViewEditor(TransactionCase):

    def setUp(self):
        super(TestBiSqlViewEditor, self).setUp()
        self.res_partner = self.env['res.partner']
        self.res_users = self.env['res.users']
        self.bi_sql_view = self.env['bi.sql.view']
        self.view = self.env.ref(
            'bi_sql_editor.partner_sql_view')
        # deleting the existing views otherwise it fails
        self.view.state = 'model_valid'
        self.view.button_set_draft()
        self.group_bi_user = self.env.ref(
            'sql_request_abstract.group_sql_request_user')
        self.group_user = self.env.ref(
            'base.group_user')
        self.company = self.env.ref('base.main_company')

    def test_process_view(self):
        self.assertEqual(self.view.state, 'draft', 'state not draft')
        self.view.button_validate_sql_expression()
        self.assertEqual(self.view.state, 'sql_valid', 'state not sql_valid')
        self.view._check_execution()
        for field in self.view.bi_sql_view_field_ids:
            field.graph_type = 'row'
        self.view.button_create_sql_view_and_model()
        self.assertEqual(self.view.state, 'model_valid',
                         'state not model_valid')
        self.view.button_create_ui()
        self.assertEqual(self.view.state, 'ui_valid', 'state not ui_valid')
        self.view.button_open_view()
        self.view.button_set_draft()

    def test_copy(self):
        self.assertEqual(self.view.mod, 'draft', 'state not draft')
        copy_view = self.view.copy()
        self.assertEqual(copy_view.name, 'Partners View (Copy)', 'Wrong name')

    def test_unlink(self):
        self.assertEqual(self.view.state, 'draft', 'state not draft')
        self.view.button_validate_sql_expression()
        self.view.button_create_sql_view_and_model()
        with self.assertRaises(UserError):
            self.view.unlink()
        self.view.button_set_draft()
        self.view.unlink()
