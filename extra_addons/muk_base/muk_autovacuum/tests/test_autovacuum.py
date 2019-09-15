###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Autovacuum 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import logging
import datetime

from odoo.tests import common

_logger = logging.getLogger(__name__)

class AutoVacuumTestCase(common.TransactionCase):
    
    def setUp(self):
        super(AutoVacuumTestCase, self).setUp()
        self.logs = self.env['ir.logging']
        self.rules = self.env['muk_autovacuum.rules']
        self.model_model = self.env['ir.model']
        self.model_fields = self.env['ir.model.fields']
        self.model_logs = self.model_model.search([('model', '=', 'ir.logging')], limit=1)
        time_field_domain = [
            ('model_id', '=', self.model_logs.id),
            ('ttype', '=', 'datetime'),
            ('name', '=', 'create_date')]
        self.time_field_logs = self.model_fields.search(time_field_domain, limit=1)
    
    def test_autovacuum_time(self):
        self.create_logs()
        self.rules.create({
            'name': "Delete Logs after 1 Minute",
            'state': 'time',
            'model': self.model_logs.id,
            'time_field': self.time_field_logs.id,
            'time_type': 'minutes',
            'time': 1})
        self.run_autovacuum()
        
    def test_autovacuum_size(self):
        self.create_logs()
        self.rules.create({
            'name': "Delete Logs Count > 1",
            'state': 'size',
            'model': self.model_logs.id,
            'size': 1,
            'size_order': "id desc",
            'size_type': 'fixed'})
        self.run_autovacuum()
        
    def test_autovacuum_domain(self):
        self.create_logs()
        self.rules.create({
            'name': "Delete Logs with Domain",
            'state': 'domain',
            'model': self.model_logs.id,
            'domain': "[]"})
        self.run_autovacuum()
    
    def create_logs(self):
        ids = []
        time = datetime.datetime.utcnow()
        for index in range(0, 10):
            log = self.logs.create({
                'create_date': time - datetime.timedelta(days=index),
                'create_uid': self.env.user.id,
                'name': "Test %s" % index,
                'type': 'server',
                'dbname': self.env.cr.dbname,
                'level': "INFO",
                'message': "TEST",
                'path': "PATH",
                'func': "TEST",
                'line': 1})
            ids.append(log.id)
        return ids
    
    def run_autovacuum(self):
        count_before = self.env['ir.logging'].search([], count=True)
        self.env['ir.cron'].search([('model_id', '=', 'ir.autovacuum')]).ir_actions_server_id.run()
        count_after = self.env['ir.logging'].search([], count=True)
        self.assertTrue(count_before > count_after)
        