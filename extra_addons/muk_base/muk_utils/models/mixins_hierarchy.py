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

import json
import operator
import functools
import collections

from odoo import models, fields, api
from odoo.osv import expression

class Hierarchy(models.AbstractModel):
    
    _name = 'muk_utils.mixins.hierarchy'
    _description = 'Hierarchy Mixin'
    
    _parent_store = True
    _parent_path_sudo = False
    _parent_path_store = False
    
    _name_path_context = "show_path"
    
    #----------------------------------------------------------
    # Database
    #----------------------------------------------------------
    
    parent_path = fields.Char(
        string="Parent Path", 
        index=True)
    
    @api.model
    def _add_magic_fields(self):
        super(Hierarchy, self)._add_magic_fields()
        def add(name, field):
            if name not in self._fields:
                self._add_field(name, field)
        path_names_search = None
        if not self._parent_path_store:
            path_names_search = '_search_parent_path_names'
        add('parent_path_names', fields.Char(
            _module=self._module,
            compute='_compute_parent_paths',
            compute_sudo=self._parent_path_sudo,
            store=self._parent_path_store,
            search=path_names_search,
            string="Path Names",
            readonly=True,
            automatic=True))
        add('parent_path_json', fields.Text(
            _module=self._module,
            compute='_compute_parent_paths',
            compute_sudo=self._parent_path_sudo,
            store=self._parent_path_store,
            string="Path Json",
            readonly=True,
            automatic=True))

    #----------------------------------------------------------
    # Helper
    #----------------------------------------------------------

    def _get_depends_parent_paths(self):
        depends = ['parent_path']
        if self._rec_name:
            depends += [self._rec_name]
        elif 'name' in self._fields:
            depends += ['name']
        elif 'x_name' in self._fields:
            depends += ['x_name']
        return depends

    #----------------------------------------------------------
    # Search
    #----------------------------------------------------------
    
    @api.model
    def _search_parent_path_names(self, operator, operand):
        domain = []
        for value in operand.split('/'):
            args = [(self._rec_name_fallback(), operator, value)]
            domain = expression.OR([args, domain]) if domain else args
        return domain if domain else [(self._rec_name_fallback(), operator, "")]

    #----------------------------------------------------------
    # Read, View 
    #----------------------------------------------------------
    
    @api.depends(lambda self: self._get_depends_parent_paths())
    def _compute_parent_paths(self):
        records = self.filtered(lambda record: record.parent_path)
        paths = [list(map(int, rec.parent_path.split('/')[:-1])) for rec in records]
        ids = paths and set(functools.reduce(operator.concat, paths)) or []
        model_without_path = self.with_context(**{self._name_path_context: False})
        filtered_records = model_without_path.browse(ids)._filter_access('read')
        data = dict(filtered_records.name_get())
        for record in records:
            path_names = [""]
            path_json = []
            for id in reversed(list(map(int, record.parent_path.split('/')[:-1]))):
                if id not in data:
                    break
                path_names.append(data[id])
                path_json.append({
                    'model': record._name,
                    'name': data[id],
                    'id': id,
                })
            path_names.reverse()
            path_json.reverse()
            record.update({
                'parent_path_names': '/'.join(path_names),
                'parent_path_json': json.dumps(path_json),
            })
    
    @api.model
    def _name_search(self, name='', args=None, operator='ilike', limit=100, name_get_uid=None):
        domain = list(args or [])
        if not (name == '' and operator == 'ilike') :
            if '/' in name:
                domain += [('parent_path_names', operator, name)]  
            else:
                domain += [(self._rec_name, operator, name)]
        records = self.browse(self._search(domain, limit=limit, access_rights_uid=name_get_uid))
        return models.lazy_name_get(records.sudo(name_get_uid or self.env.uid)) 
    
    @api.multi
    def name_get(self):
        if self.env.context.get(self._name_path_context):
            res = []
            for record in self:
                names = record.parent_path_names
                if not names:
                    res.append(super(Hierarchy, record).name_get()[0])
                elif not len(names) > 50:
                    res.append((record.id, names))
                else:
                    res.append((record.id, ".." + names[-48:]))
            return res
        return super(Hierarchy, self).name_get()
    
    #----------------------------------------------------------
    # Create, Update, Delete
    #----------------------------------------------------------
    
    @api.multi
    def write(self, vals):
        if self._parent_path_store and self._rec_name_fallback() in vals:
            with self.env.norecompute():
                res = super(Hierarchy, self).write(vals)
                domain = [('id', 'child_of', self.ids)]
                records = self.sudo().search(domain)
                records.modified(['parent_path'])
            if self.env.recompute and self.env.context.get('recompute', True):
                records.recompute()
            return res  
        return super(Hierarchy, self).write(vals)        
            