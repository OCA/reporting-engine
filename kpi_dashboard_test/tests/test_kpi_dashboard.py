# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase
from odoo.exceptions import ValidationError
from odoo.tests.common import Form


class TestKpiDashboard(TransactionCase):

    def setUp(self):
        super(TestKpiDashboard, self).setUp()
        self.kpi_01 = self.env['kpi.kpi'].create({
            'name': 'KPI 01',
            'computation_method': 'function',
            'widget': 'number',
            'function': 'test_demo_number'
        })
        self.kpi_02 = self.env['kpi.kpi'].create({
            'name': 'KPI 02',
            'computation_method': 'function',
            'widget': 'number',
            'function': 'test_demo_number'
        })
        self.dashboard = self.env['kpi.dashboard'].create({
            'name': 'Dashboard',
            'number_of_columns': 4,
            'widget_dimension_x': 250,
            'widget_dimension_y': 250,
        })
        self.env['kpi.dashboard.item'].create({
            'dashboard_id': self.dashboard.id,
            'kpi_id': self.kpi_01.id,
            'name': self.kpi_01.name,
            'row': 1,
            'column': 1,
        })
        self.env['kpi.dashboard.item'].create({
            'dashboard_id': self.dashboard.id,
            'name': self.kpi_02.name,
            'kpi_id': self.kpi_02.id,
            'row': 1,
            'column': 2,
        })
        self.env['kpi.dashboard.item'].create({
            'dashboard_id': self.dashboard.id,
            'name': 'TITLE',
            'row': 2,
            'column': 1,
        })

    def test_constrains_01(self):
        with self.assertRaises(ValidationError):
            self.kpi_01.dashboard_item_ids.write({'size_x': 2})

    def test_constrains_02(self):
        with self.assertRaises(ValidationError):
            self.kpi_02.dashboard_item_ids.write({'size_x': 4})

    def test_constrains_03(self):
        with self.assertRaises(ValidationError):
            self.kpi_01.dashboard_item_ids.write({'size_y': 11})

    def test_menu(self):
        self.assertFalse(self.dashboard.menu_id)
        wzd = self.env['kpi.dashboard.menu'].create({
            'dashboard_id': self.dashboard.id,
            'menu_id': self.env['ir.ui.menu'].search([], limit=1).id,
        })
        wzd.generate_menu()
        self.assertTrue(self.dashboard.menu_id)
        self.assertFalse(self.dashboard.menu_id.groups_id)
        self.dashboard.write({
            'group_ids': [
                (6, 0, self.env['res.groups'].search([], limit=1).ids)]
        })
        self.assertTrue(self.dashboard.menu_id.groups_id)

    def test_onchange(self):
        with Form(self.env['kpi.dashboard']) as dashboard:
            dashboard.name = 'New Dashboard'
            with dashboard.item_ids.new() as item:
                item.kpi_id = self.kpi_01
                self.assertTrue(item.name)

    def test_read_dashboard(self):
        data = self.dashboard.read_dashboard()
        title_found = False
        actions = 0
        for item in data['item_ids']:
            if not item.get('kpi_id'):
                title_found = True
            if item.get('actions', False):
                actions += len(item['actions'])
        self.assertTrue(title_found)
        self.assertEqual(0, actions)
        act01 = self.env['ir.actions.act_window'].search(
            [], limit=1)
        self.env['kpi.kpi.action'].create({
            'kpi_id': self.kpi_01.id,
            'action': '%s,%s' % (act01._name, act01.id)
        })
        act02 = self.env['ir.actions.act_url'].search(
            [], limit=1)
        self.env['kpi.kpi.action'].create({
            'kpi_id': self.kpi_01.id,
            'action': '%s,%s' % (act02._name, act02.id)
        })
        data = self.dashboard.read_dashboard()
        title_found = False
        actions = 0
        for item in data['item_ids']:
            if not item.get('kpi_id'):
                title_found = True
            if item.get('actions', False):
                actions += len(item['actions'])
        self.assertTrue(title_found)
        self.assertEqual(2, actions)

    def test_compute(self):
        self.assertFalse(self.kpi_01.value_last_update)
        self.kpi_01.compute()
        self.assertTrue(self.kpi_01.value_last_update)
