###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Utils 
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

from odoo import api, models, fields
from odoo.osv import expression

from odoo.addons.muk_utils.tools import utils

_logger = logging.getLogger(__name__)

class Base(models.AbstractModel):
    
    _inherit = 'base'
    
    #----------------------------------------------------------
    # Helper Methods
    #----------------------------------------------------------
    
    @api.model
    def _check_parent_field(self):
        if self._parent_name not in self._fields:
            raise TypeError("The parent (%s) field does not exist." % self._parent_name)
    
    @api.model
    def _build_search_childs_domain(self, parent_id, domain=[]):
        self._check_parent_field()
        parent_domain = [[self._parent_name, '=', parent_id]]
        return expression.AND([parent_domain, domain]) if domain else parent_domain
    
    @api.model
    def _check_context_bin_size(self, field):
        return any(key in self.env.context for key in ['bin_size', 'bin_size_%s' % (field)])
    
    #----------------------------------------------------------
    # Security
    #----------------------------------------------------------
    
    @api.multi
    def _filter_access(self, operation):
        if self.check_access_rights(operation, False):
            return self._filter_access_rules(operation)
        return self.env[self._name]
    
    @api.multi
    def _filter_access_ids(self, operation):
        return self._filter_access(operation).ids
    
    @api.multi
    def check_access(self, operation, raise_exception=False):
        try:
            access_right = self.check_access_rights(operation, raise_exception)
            access_rule = self.check_access_rule(operation) is None
            return access_right and access_rule
        except AccessError:
            if raise_exception:
                raise
            return False
        
    #----------------------------------------------------------
    # Hierarchy Methods
    #----------------------------------------------------------
    
    @api.model
    def search_parents(self, domain=[], offset=0, limit=None, order=None, count=False):
        """ This method finds the top level elements of the hierarchy for a given search query.
            
            :param domain: a search domain <reference/orm/domains> (default: empty list)
            :param order: a string to define the sort order of the query (default: none)
            :returns: the top level elements for the given search query 
        """
        res = self._search_parents(domain=domain, offset=offset, limit=limit, order=order, count=count)
        return res if count else self.browse(res)
    
    @api.model
    def search_read_parents(self, domain=[], fields=None, offset=0, limit=None, order=None):
        """ This method finds the top level elements of the hierarchy for a given search query.
            
            :param domain: a search domain <reference/orm/domains> (default: empty list)
            :param fields: a list of fields to read (default: all fields of the model)
            :param order: a string to define the sort order of the query (default: none)
            :returns: the top level elements for the given search query 
        """
        records = self.search_parents(domain=domain, offset=offset, limit=limit, order=order)
        if not records:
            return []
        if fields and fields == ['id']:
            return [{'id': record.id} for record in records]
        result = records.read(fields)
        if len(result) <= 1:
            return result
        index = {vals['id']: vals for vals in result}
        return [index[record.id] for record in records if record.id in index]
    
    @api.model
    def _search_parents(self, domain=[], offset=0, limit=None, order=None, count=False):
        self._check_parent_field()
        self.check_access_rights('read')
        if expression.is_false(self, domain):
            return []
        query = self._where_calc(domain)
        self._apply_ir_rules(query, 'read')
        from_clause, where_clause, where_clause_arguments = query.get_sql()
        parent_where = where_clause and (" WHERE %s" % where_clause) or ''
        parent_query = 'SELECT "%s".id FROM ' % self._table + from_clause + parent_where
        no_parent_clause ='"{table}"."{field}" IS NULL'.format(
            table=self._table, 
            field=self._parent_name
        )
        no_access_clause ='"{table}"."{field}" NOT IN ({query})'.format(
            table=self._table,
            field=self._parent_name,
            query=parent_query
        )
        parent_clause = '({0} OR {1})'.format(
            no_parent_clause,
            no_access_clause
        )
        order_by = self._generate_order_by(order, query)
        from_clause, where_clause, where_clause_params = query.get_sql()
        where_str = (
            where_clause and 
            (" WHERE %s AND %s" % (where_clause, parent_clause)) or 
            (" WHERE %s" % parent_clause)
        )
        if count:
            query_str = 'SELECT count(1) FROM ' + from_clause + where_str
            self._cr.execute(query_str, where_clause_params)
            return self._cr.fetchone()[0]
        limit_str = limit and ' limit %d' % limit or ''
        offset_str = offset and ' offset %d' % offset or ''
        query_str = 'SELECT "%s".id FROM ' % self._table + from_clause + where_str + order_by + limit_str + offset_str
        complete_where_clause_params = where_clause_params + where_clause_arguments
        self._cr.execute(query_str, complete_where_clause_params)
        return utils.uniquify_list([x[0] for x in self._cr.fetchall()])
    
    @api.model
    def search_childs(self, parent_id, domain=[], offset=0, limit=None, order=None, count=False):
        """ This method finds the direct child elements of the parent record for a given search query.
            
            :param parent_id: the integer representing the ID of the parent record
            :param domain: a search domain <reference/orm/domains> (default: empty list)
            :param offset: the number of results to ignore (default: none)
            :param limit: maximum number of records to return (default: all)
            :param order: a string to define the sort order of the query (default: none)
            :param count: counts and returns the number of matching records (default: False)
            :returns: the top level elements for the given search query 
        """
        domain = self._build_search_childs_domain(parent_id, domain=domain)
        return self.search(domain, offset=offset, limit=limit, order=order, count=count)
    
    @api.model
    def search_read_childs(self, parent_id, domain=[], fields=None, offset=0, limit=None, order=None):
        """ This method finds the direct child elements of the parent record for a given search query.
            
            :param parent_id: the integer representing the ID of the parent record
            :param domain: a search domain <reference/orm/domains> (default: empty list)
            :param fields: a list of fields to read (default: all fields of the model)
            :param offset: the number of results to ignore (default: none)
            :param limit: maximum number of records to return (default: all)
            :param order: a string to define the sort order of the query (default: none)
            :returns: the top level elements for the given search query 
        """
        domain = self._build_search_childs_domain(parent_id, domain=domain)
        return self.search_read(domain=domain, fields=fields, offset=offset, limit=limit, order=order)
        