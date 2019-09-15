###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Security 
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

from collections import defaultdict

from odoo import _, models, api, fields, SUPERUSER_ID
from odoo.exceptions import AccessError
from odoo.osv import expression

from odoo.addons.muk_security.tools.security import NoSecurityUid

_logger = logging.getLogger(__name__)

class AccessGroupsModel(models.AbstractModel):
    
    _name = 'muk_security.mixins.access_groups'
    _description = "Group Access Mixin"
    _inherit = 'muk_security.mixins.access_rights'
    
    # If set the group fields are restricted by the access group
    _access_groups_fields = None
    
    # If set the group fields are recomputed as super administrator
    _access_groups_sudo = False
    
    # Set it to True to enforced security even if no group has been set
    _access_groups_strict = False
    
    # Set it to True to let the non strict mode check for existing groups per mode
    _access_groups_mode = False
     
    #----------------------------------------------------------
    # Datebase 
    #----------------------------------------------------------

    @api.model
    def _add_magic_fields(self):
        super(AccessGroupsModel, self)._add_magic_fields()
        def add(name, field):
            if name not in self._fields:
                self._add_field(name, field)
        add('groups', fields.Many2many(
            _module=self._module,
            comodel_name='muk_security.access_groups',
            relation='%s_groups_rel' % (self._table),
            column1='aid',
            column2='gid',
            string="Groups",
            automatic=True,
            groups=self._access_groups_fields))
        add('complete_groups', fields.Many2many(
            _module=self._module,
            comodel_name='muk_security.access_groups',
            relation='%s_complete_groups_rel' % (self._table),
            column1='aid',
            column2='gid',
            string="Complete Groups", 
            compute='_compute_groups',
            readonly=True,
            store=True,
            automatic=True,
            compute_sudo=self._access_groups_sudo,
            groups=self._access_groups_fields))
    
    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------

    @api.multi
    def _filter_access(self, operation):
        records = super(AccessGroupsModel, self)._filter_access(operation)
        return records.filter_access_groups(operation)
    
    @api.model
    def _apply_access_groups(self, query, mode='read'):
        if self.env.user.id == SUPERUSER_ID or isinstance(self.env.uid, NoSecurityUid):
            return None
        where_clause = '''
            "{table}".id IN ( 
                SELECT r.aid 
                FROM {table}_complete_groups_rel r 
                JOIN muk_security_access_groups g ON r.gid = g.id 
                JOIN muk_security_access_groups_users_rel u ON r.gid = u.gid 
                WHERE u.uid = %s AND g.perm_{mode} = true 
            ) 
        '''.format(table=self._table, mode=mode)
        if not self._access_groups_strict:
            exists_clause = '''
                NOT EXISTS ( 
                    SELECT 1 
                        FROM {table}_complete_groups_rel r 
                        JOIN muk_security_access_groups g ON r.gid = g.id 
                        WHERE r.aid = "{table}".id {groups_mode} 
                ) 
            '''
            groups_mode = self._access_groups_mode and 'AND g.perm_{mode} = true'.format(mode=mode)
            exists_clause = exists_clause.format(table=self._table, groups_mode=groups_mode or "")  
            where_clause = '({groups_clause} OR {exists_clause})'.format(
                groups_clause=where_clause,
                exists_clause=exists_clause,
            )
        query.where_clause += [where_clause]
        query.where_clause_params += [self.env.user.id]
    
    @api.model
    def _apply_ir_rules(self, query, mode='read'):
        super(AccessGroupsModel, self)._apply_ir_rules(query, mode=mode)
        self._apply_access_groups(query, mode=mode)
        
    @api.multi
    def _get_ids_without_access_groups(self, operation):
        sql_query = '''
            SELECT id 
            FROM {table} a 
            WHERE NOT EXISTS ( 
                SELECT 1 
                FROM {table}_complete_groups_rel r 
                JOIN muk_security_access_groups g ON r.gid = g.id 
                WHERE r.aid = a.id {subset} {groups_mode} 
            ); 
        '''
        subset = self.ids and 'AND r.aid = ANY (VALUES {ids})'.format(
            ids=', '.join(map(lambda id: '(%s)' % id, self.ids))
        )
        groups_mode = self._access_groups_mode and 'AND g.perm_{operation} = true'.format(
            operation=operation
        )
        sql_query = sql_query.format(
            table=self._table,
            subset=subset or "",
            groups_mode=groups_mode or "",
        )  
        self.env.cr.execute(sql_query)
        return list(map(lambda val: val[0], self.env.cr.fetchall()))
          
    #----------------------------------------------------------
    # Function
    #----------------------------------------------------------

    @api.multi
    def check_access(self, operation, raise_exception=False):
        res = super(AccessGroupsModel, self).check_access(operation, raise_exception)
        try:
            return res and self.check_access_groups(operation) == None
        except AccessError:
            if raise_exception:
                raise
            return False
    
    #----------------------------------------------------------
    # Security
    #----------------------------------------------------------

    @api.multi
    def check_access_groups(self, operation):
        if self.env.user.id == SUPERUSER_ID or isinstance(self.env.uid, NoSecurityUid):
            return None
        group_ids = set(self.ids) - set(self._get_ids_without_access_groups(operation))
        if group_ids:
            sql_query = '''
                SELECT r.aid, perm_{operation}       
                FROM {table}_complete_groups_rel r 
                JOIN muk_security_access_groups g ON r.gid = g.id 
                JOIN muk_security_access_groups_users_rel u ON r.gid = u.gid 
                WHERE r.aid = ANY (VALUES {ids}) AND u.uid = %s;
            '''.format(
                operation=operation,
                table=self._table,
                ids=', '.join(map(lambda id: '(%s)' % id, group_ids)),
            )
            self.env.cr.execute(sql_query, [self.env.user.id])
            result = defaultdict(list)
            for key, val in self.env.cr.fetchall(): 
                result[key].append(val)
            if len(result.keys()) < len(group_ids) or not all(list(map(lambda val: any(val), result.values()))):
                raise AccessError(_(
                    'The requested operation cannot be completed due to group security restrictions. '
                    'Please contact your system administrator.\n\n(Document type: %s, Operation: %s)'
                ) % (self._description, operation))
                
    @api.multi
    def filter_access_groups(self, operation):
        if self.env.user.id == SUPERUSER_ID or isinstance(self.env.uid, NoSecurityUid):
            return self
        ids_with_access = self._get_ids_without_access_groups(operation)
        group_ids = set(self.ids) - set(ids_with_access)
        if group_ids:
            sql_query = '''
                SELECT r.aid 
                FROM {table}_complete_groups_rel r 
                JOIN muk_security_access_groups g ON r.gid = g.id 
                JOIN muk_security_access_groups_users_rel u ON r.gid = u.gid 
                WHERE r.aid = ANY (VALUES {ids}) AND u.uid = %s AND g.perm_{operation} = true; 
            '''.format(
                table=self._table,
                ids=', '.join(map(lambda id: '(%s)' % id, group_ids)),
                operation=operation,
            )
            self.env.cr.execute(sql_query, [self.env.user.id])
            ids_with_access += list(map(lambda val: val[0], self.env.cr.fetchall()))
        return self & self.browse(ids_with_access)

    #----------------------------------------------------------
    # Create, Update, Delete 
    #----------------------------------------------------------
    
    @api.multi
    def _write(self, vals):
        self.check_access_groups('write')
        return super(AccessGroupsModel, self)._write(vals)

    @api.multi
    def unlink(self):
        self.check_access_groups('unlink')
        return super(AccessGroupsModel, self).unlink()
    
    #----------------------------------------------------------
    # Groups
    #----------------------------------------------------------
    
    @api.depends('groups')
    def _compute_groups(self):
        for record in self:
            record.complete_groups = record.groups