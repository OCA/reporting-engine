# -*- coding: utf-8 -*-
# Copyright 2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp.tests.common import TransactionCase, at_install, post_install
from openerp.exceptions import AccessError


class TestBiSqlViewEditor(TransactionCase):

    def setUp(self):
        super(TestBiSqlViewEditor, self).setUp()
        self.res_partner = self.env['res.partner']
        self.res_users = self.env['res.users']
        self.bi_sql_view = self.env['bi.sql.view']
        self.group_bi_user = self.env.ref(
            'sql_request_abstract.group_sql_request_manager')
        self.group_user = self.env.ref(
            'base.group_user')
        self.view = self.bi_sql_view.create({
            'name': 'Partners View 2',
            'is_materialized': False,
            'technical_name': 'partners_view_2',
            'query': "SELECT name as x_name, street as x_street,"
                     "company_id as x_company_id FROM res_partner "
                     "ORDER BY name"
        })
        self.company = self.env.ref('base.main_company')
        # Create bi user
        self.bi_user = self._create_user('bi_user', [self.group_bi_user],
                                         self.company)
        self.no_bi_user = self._create_user('no_bi_user', [self.group_user],
                                            self.company)

    def _create_user(self, login, groups, company):
        """Create a user."""
        group_ids = [group.id for group in groups]
        user = self.res_users.create({
            'name': 'Test BI User',
            'login': login,
            'password': 'demo',
            'email': 'example@yourcompany.com',
            'company_id': company.id,
            'groups_id': [(6, 0, group_ids)]
        })
        return user

    @at_install(False)
    @post_install(True)
    def test_process_view(self):
        view = self.view
        self.assertEqual(view.state, 'draft', 'state not draft')
        view.button_validate_sql_expression()
        self.assertEqual(view.state, 'sql_valid', 'state not sql_valid')

    def test_copy(self):
        copy_view = self.view.copy()
        self.assertEqual(
            copy_view.name, 'Partners View 2 (Copy)', 'Wrong name')

    def test_security(self):
        with self.assertRaises(AccessError):
            self.bi_sql_view.sudo(self.no_bi_user.id).search(
                [('name', '=', 'Partners View 2')])
        bi = self.bi_sql_view.sudo(self.bi_user.id).search(
            [('name', '=', 'Partners View 2')])
        self.assertEqual(len(bi), 1, 'Bi user should not have access to '
                                     'bi %s' % self.view.name)

    def test_unlink(self):
        self.assertEqual(self.view.state, 'draft', 'state not draft')
        self.view.button_validate_sql_expression()
        self.view.unlink()
        res = self.bi_sql_view.search([('name', '=', 'Partners View 2')])
        self.assertEqual(len(res), 0, 'View not deleted')
