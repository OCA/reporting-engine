# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openerp import api, models
from openerp.modules.registry import RegistryManager

NO_BI_MODELS = [
    'temp.range',
    'account.statement.operation.template',
    'fetchmail.server'
]

NO_BI_FIELDS = [
    'id',
    'create_uid',
    'create_date',
    'write_uid',
    'write_date'
]

NO_BI_TTYPES = [
    'many2many',
    'one2many',
    'html',
    'binary',
    'reference'
]


def dict_for_field(field):
    return {
        'id': field.id,
        'name': field.name,
        'description': field.field_description,
        'type': field.ttype,
        'relation': field.relation,
        'custom': False,
        'model_id': field.model_id.id,
        'model': field.model_id.model,
        'model_name': field.model_id.name
    }


class IrModel(models.Model):
    _inherit = 'ir.model'

    @api.model
    def _filter_bi_fields(self, ir_model_field_obj):
        name = ir_model_field_obj.name
        model = ir_model_field_obj.model_id
        model_name = model.model
        if model_name[0:6] != 'x_bve.':
            Model = self.env[model_name]
            if name in Model._columns:
                f = Model._columns[name]
                return f._classic_write
        return False

    @api.model
    def _filter_bi_models(self, model):

        def _check_name(model_model):
            if model_model in NO_BI_MODELS:
                return 1
            return 0

        def _check_startswith(model_model):
            if model_model.startswith('workflow') or \
                    model_model.startswith('ir.') or \
                    model_model.startswith('base_'):
                return 1
            return 0

        def _check_contains(model_model):
            if 'mail' in model_model or \
                    '_' in model_model or \
                    'report' in model_model or \
                    'edi.' in model_model:
                return 1
            return 0

        def _check_unknow(model_name):
            if model_name == 'Unknow' or '.' in model_name:
                return 1
            return 0

        model_model = model['model']
        model_name = model['name']
        count_check = 0
        count_check += _check_name(model_model)
        count_check += _check_startswith(model_model)
        count_check += _check_contains(model_model)
        count_check += _check_unknow(model_name)
        if not count_check:
            return self.env['ir.model.access'].check(
                model['model'], 'read', False)
        return False

    @api.model
    def get_related_fields(self, model_ids):
        """ Return list of field dicts for all fields that can be
            joined with models in model_ids
        """
        Model = self.env['ir.model']
        domain = [('id', 'in', model_ids.values())]
        models = Model.sudo().search(domain)
        model_names = {}
        for model in models:
            model_names.update({model.id: model.model})

        related_fields = self._get_related_fields_list(model_ids, model_names)
        return related_fields

    @api.model
    def _get_related_fields_list(self, model_ids, model_names):

        def _get_right_fields(model_ids, model_names):
            Fields = self.env['ir.model.fields']
            rfields = []
            domain = [('model_id', 'in', model_ids.values()),
                      ('ttype', 'in', ['many2one'])]
            for field in filter(
                    self._filter_bi_fields,
                    Fields.sudo().search(domain)):
                for model in model_ids.items():
                    if model[1] == field.model_id.id:
                        rfields.append(
                            dict(dict_for_field(field),
                                 join_node=-1,
                                 table_alias=model[0])
                        )
            return rfields

        def _get_left_fields(model_ids, model_names):
            Fields = self.env['ir.model.fields']
            lfields = []
            domain = [('relation', 'in', model_names.values()),
                      ('ttype', 'in', ['many2one'])]
            for field in filter(
                    self._filter_bi_fields,
                    Fields.sudo().search(domain)):
                for model in model_ids.items():
                    if model_names[model[1]] == field['relation']:
                        lfields.append(
                            dict(dict_for_field(field),
                                 join_node=model[0],
                                 table_alias=-1)
                        )
            return lfields

        def _get_relation_list(model_ids, model_names, lfields):
            relation_list = []
            for model in model_ids.items():
                for field in lfields:
                    if model_names[model[1]] == field['relation']:
                        relation_list.append(
                            dict(field, join_node=model[0])
                        )
            return relation_list

        def _get_model_list(model_ids, rfields):
            model_list = []
            for model in model_ids.items():
                for field in rfields:
                    if model[1] == field['model_id']:
                        model_list.append(
                            dict(field, table_alias=model[0])
                        )
            return model_list

        lfields = _get_left_fields(model_ids, model_names)
        rfields = _get_right_fields(model_ids, model_names)

        relation_list = _get_relation_list(model_ids, model_names, lfields)
        model_list = _get_model_list(model_ids, rfields)

        related_fields = relation_list + model_list
        return related_fields

    @api.model
    def get_related_models(self, model_ids):
        """ Return list of model dicts for all models that can be
            joined with models in model_ids
        """
        def _get_field(fields, orig, target):
            field_list = []
            for f in fields:
                if f[orig] == -1:
                    field_list.append(f[target])
            return field_list

        def _get_list_id(model_ids, fields):
            list_model = model_ids.values()
            list_model += _get_field(fields, 'table_alias', 'model_id')
            return list_model

        def _get_list_relation(fields):
            list_model = _get_field(fields, 'join_node', 'relation')
            return list_model

        models_list = []
        related_fields = self.get_related_fields(model_ids)
        list_id = _get_list_id(model_ids, related_fields)
        list_model = _get_list_relation(related_fields)
        domain = ['|',
                  ('id', 'in', list_id),
                  ('model', 'in', list_model)]
        models = self.env['ir.model'].sudo().search(domain)
        for model in models:
            models_list.append({
                'id': model.id,
                'name': model.name,
                'model': model.model
            })
        return sorted(
            filter(self._filter_bi_models, models_list),
            key=lambda x: x['name']
        )

    @api.model
    def get_models(self):
        """ Return list of model dicts for all available models.
        """
        def dict_for_model(model):
            return {
                'id': model.id,
                'name': model.name,
                'model': model.model
            }

        models_domain = [('osv_memory', '=', False)]
        return sorted(filter(
            self._filter_bi_models,
            [dict_for_model(model)
                for model in self.search(models_domain)]),
            key=lambda x: x['name'])

    @api.model
    def get_join_nodes(self, field_data, new_field):
        """ Return list of field dicts of join nodes

            Return all possible join nodes to add new_field to the query
            containing model_ids.
        """
        def _get_model_ids(field_data):
            model_ids = dict([(field['table_alias'],
                               field['model_id']) for field in field_data])
            return model_ids

        def _get_join_nodes_dict(model_ids, new_field):
            join_nodes = []
            for alias, model_id in model_ids.items():
                if model_id == new_field['model_id']:
                    join_nodes.append({'table_alias': alias})
            for dict_field in self.get_related_fields(model_ids):
                condition = [
                    dict_field['join_node'] == -1,
                    dict_field['table_alias'] == -1
                ]
                relation = (new_field['model'] == dict_field['relation'])
                model = (new_field['model_id'] == dict_field['model_id'])
                if (relation and condition[0]) or (model and condition[1]):
                    join_nodes.append(dict_field)
            return join_nodes

        def remove_duplicate_nodes(join_nodes):
            seen = set()
            nodes_list = []
            for node in join_nodes:
                node_tuple = tuple(node.items())
                if node_tuple not in seen:
                    seen.add(node_tuple)
                    nodes_list.append(node)
            return nodes_list

        model_ids = _get_model_ids(field_data)
        keys = [(field['table_alias'], field['id'])
                for field in field_data if field.get('join_node', -1) != -1]
        join_nodes = _get_join_nodes_dict(model_ids, new_field)
        join_nodes = remove_duplicate_nodes(join_nodes)

        return filter(
            lambda x: 'id' not in x or
                      (x['table_alias'], x['id']) not in keys, join_nodes)

    @api.model
    def get_fields(self, model_id):
        bi_field_domain = [
            ('model_id', '=', model_id),
            ('name', 'not in', NO_BI_FIELDS),
            ('ttype', 'not in', NO_BI_TTYPES)
        ]
        Fields = self.env['ir.model.fields']
        fields = filter(
            self._filter_bi_fields,
            Fields.sudo().search(bi_field_domain)
        )
        fields_dict = []
        for field in fields:
            fields_dict.append(
                {'id': field.id,
                 'model_id': model_id,
                 'name': field.name,
                 'description': field.field_description,
                 'type': field.ttype,
                 'custom': False,
                 'model': field.model_id.model,
                 'model_name': field.model_id.name
                 }
            )
        sorted_fields = sorted(
            fields_dict,
            key=lambda x: x['description'],
            reverse=True
        )
        return sorted_fields

    @api.model
    def create(self, vals):
        if self._context and self._context.get('bve'):
            vals['state'] = 'base'
        res = super(IrModel, self).create(vals)

        # this sql update is necessary since a write method here would
        # be not working (an orm constraint is restricting the modification
        # of the state field while updating ir.model)
        q = ("""UPDATE ir_model SET state = 'manual'
               WHERE id = """ + str(res.id))
        self.env.cr.execute(q)

        # update registry
        if self._context.get('bve'):

            # add model in registry
            self.instanciate(vals['model'])
            self.pool.setup_models(self.env.cr, partial=(not self.pool.ready))

            # signal that registry has changed
            RegistryManager.signal_registry_change(self.env.cr.dbname)

        return res
