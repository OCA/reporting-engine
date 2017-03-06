# -*- coding: utf-8 -*-
# Copyright 2015-2017 Onestein (<http://www.onestein.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, models

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


def dict_for_model(model):
    return {
        'id': model.id,
        'name': model.name,
        'model': model.model
    }


class IrModel(models.Model):
    _inherit = 'ir.model'

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
    def sort_filter_models(self, models_list):
        res = sorted(
            filter(self._filter_bi_models, models_list),
            key=lambda x: x['name'])
        return res

    @api.model
    def _search_fields(self, domain):
        Fields = self.env['ir.model.fields']
        fields = Fields.sudo().search(domain)
        return fields

    @api.model
    def get_related_fields(self, model_ids):
        """ Return list of field dicts for all fields that can be
            joined with models in model_ids
        """

        def get_model_list(model_ids):
            model_list = []
            domain = [('model_id', 'in', model_ids.values()),
                      ('store', '=', True),
                      ('ttype', 'in', ['many2one'])]
            filtered_fields = self._search_fields(domain)
            for model in model_ids.items():
                for field in filtered_fields:
                    if model[1] == field.model_id.id:
                        model_list.append(
                            dict(dict_for_field(field),
                                 join_node=-1,
                                 table_alias=model[0])
                        )
            return model_list

        def get_relation_list(model_ids, model_names):
            relation_list = []
            domain = [('relation', 'in', model_names.values()),
                      ('store', '=', True),
                      ('ttype', 'in', ['many2one'])]
            filtered_fields = self._search_fields(domain)
            for model in model_ids.items():
                for field in filtered_fields:
                    if model_names[model[1]] == field['relation']:
                        relation_list.append(
                            dict(dict_for_field(field),
                                 join_node=model[0],
                                 table_alias=-1)
                        )
            return relation_list

        models = self.sudo().browse(model_ids.values())
        model_names = {}
        for model in models:
            model_names.update({model.id: model.model})

        model_list = get_model_list(model_ids)
        relation_list = get_relation_list(model_ids, model_names)

        return relation_list + model_list

    @api.model
    def get_related_models(self, model_ids):
        """ Return list of model dicts for all models that can be
            joined with the already selected models.
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
        for model in self.sudo().search(domain):
            models_list.append(dict_for_model(model))
        return self.sort_filter_models(models_list)

    @api.model
    def get_models(self):
        """ Return list of model dicts for all available models.
        """

        models_list = []
        for model in self.search([('transient', '=', False)]):
            models_list.append(dict_for_model(model))
        return self.sort_filter_models(models_list)

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
            for field in self.get_related_fields(model_ids):
                c = [field['join_node'] == -1, field['table_alias'] == -1]
                a = (new_field['model'] == field['relation'])
                b = (new_field['model_id'] == field['model_id'])
                if (a and c[0]) or (b and c[1]):
                    join_nodes.append(field)
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
        domain = [
            ('model_id', '=', model_id),
            ('store', '=', True),
            ('name', 'not in', NO_BI_FIELDS),
            ('ttype', 'not in', NO_BI_TTYPES)
        ]
        fields_dict = []
        filtered_fields = self._search_fields(domain)
        for field in filtered_fields:
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
        q = "UPDATE ir_model SET state = 'manual' WHERE id = %s"
        self.env.cr.execute(q, (res.id, ))

        # # update registry
        if self._context.get('bve'):
            # setup models; this reloads custom models in registry
            self.pool.setup_models(self._cr, partial=(not self.pool.ready))

            # signal that registry has changed
            self.pool.signal_registry_change()

        return res
