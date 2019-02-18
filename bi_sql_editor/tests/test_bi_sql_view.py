# -*- coding: utf-8 -*-
# Copyright 2018 Therp BV <https://therp.nl>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
from openerp.tests.common import TransactionCase

QUERY = """
    SELECT
    name AS x_name, create_date AS x_create_date, parent_id AS x_parent_id
    FROM
    res_partner
    """


class TestBiSqlView(TransactionCase):

    post_install = True
    at_install = False

    def setUp(self):
        super(TestBiSqlView, self).setUp()
        bi_sql_view_model = self.env['bi.sql.view']
        res_partner_model = self.env['res.partner']
        partner1 = res_partner_model.create({'name': 'partner1'})
        res_partner_model.create({
            'name': 'partner2',
            'child_ids': [(6, 0, partner1.ids)],
        })
        self.view = bi_sql_view_model.create({
            'name': 'test_view',
            'technical_name': 'test_view',
            'is_materialized': True,
            'query': QUERY,
        })

    def test_materialized_view_creation(self):
        self.view.button_validate_sql_expression()
        self.view.button_create_sql_view_and_model()
        self.assertIsNotNone(self.view.view_name)
        self.assertIsNotNone(self.view.is_materialized)
        self.assertIsNotNone(self.view.size)
        self.assertIsNotNone(self.view.cron_id)
        self.assertIsNotNone(self.view.bi_sql_view_field_ids)
        for field in self.view.bi_sql_view_field_ids:
            if field.name == 'x_id':
                self.assertEquals(field.sql_type, 'integer')
                self.assertEquals(field.ttype, 'integer')
            elif field.name == 'x_name':
                self.assertEquals(field.sql_type, 'character varying')
                self.assertEquals(field.ttype, 'char')
            elif field.name == 'x_parent_id':
                self.assertEquals(field.sql_type, 'integer')
                self.assertEquals(field.ttype, 'many2one')
            elif field.name == 'x_create_date':
                self.assertEquals(
                    field.sql_type,
                    'timestamp without time zone',
                )
                self.assertEquals(field.ttype, 'datetime')
        self.env.cr.execute(
            "SELECT count(*) from information_schema.tables WHERE "
            "table_name = 'x_bi_sql_view_test_view'"
        )
        res = self.env.cr.fetchone()
        self.assertTrue(res)
        # ideally we should set the view to draft and then unlink it
        # but ir_model.unlink() calls RegistryManager.new() which in turn
        # reloads the modules which in turn re-runs this test and we get stuck
        # in an infinite loop
        # So we stop here.
