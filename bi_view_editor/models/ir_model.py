# Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models, registry

NO_BI_MODELS = [
    'temp.range',
    'account.statement.operation.template',
    'fetchmail.server'
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

        def _check_unknown(model_name):
            if model_name == 'Unknown' or '.' in model_name:
                return 1
            return 0

        model_model = model['model']
        model_name = model['name']
        count_check = 0
        count_check += _check_name(model_model)
        count_check += _check_startswith(model_model)
        count_check += _check_contains(model_model)
        count_check += _check_unknown(model_name)
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

    def get_model_list(self, model_table_map):
        if not model_table_map:
            return []
        domain = [('model_id', 'in', list(model_table_map.keys())),
                  ('store', '=', True),
                  ('ttype', '=', 'many2one')]
        fields = self.env['ir.model.fields'].sudo().search(domain)
        model_list = []
        for field in fields:
            for table_alias in model_table_map[field.model_id.id]:
                model_list.append(dict(
                    dict_for_field(field),
                    table_alias=table_alias,
                    join_node=-1,
                ))
        return model_list

    def get_relation_list(self, model_table_map):
        if not model_table_map:
            return []
        model_names = {}
        for model in self.sudo().browse(model_table_map.keys()):
            model_names.update({model.model: model.id})

        domain = [('relation', 'in', list(model_names.keys())),
                  ('store', '=', True),
                  ('ttype', '=', 'many2one')]
        fields = self.env['ir.model.fields'].sudo().search(domain)
        relation_list = []
        for field in fields:
            model_id = model_names[field.relation]
            for join_node in model_table_map[model_id]:
                relation_list.append(dict(
                    dict_for_field(field),
                    join_node=join_node,
                    table_alias=-1
                ))
        return relation_list

    @api.model
    def get_related_models(self, model_table_map):
        """ Return list of model dicts for all models that can be
            joined with the already selected models.
        """
        domain = [('transient', '=', False)]
        if model_table_map:
            model_list = self.get_model_list(model_table_map)
            relation_list = self.get_relation_list(model_table_map)
            model_ids = [f['model_id'] for f in relation_list + model_list]
            model_ids += list(model_table_map.keys())
            relations = [f['relation'] for f in model_list]
            domain += [
                '|', ('id', 'in', model_ids), ('model', 'in', relations)]
        return self.sudo().search(domain)

    @api.model
    def get_models(self, table_model_map=None):
        """ Return list of model dicts for all available models.
        """
        self = self.with_context(lang=self.env.user.lang)
        model_table_map = defaultdict(list)
        for k, v in (table_model_map or {}).items():
            model_table_map[v].append(k)

        models_list = []
        for model in self.get_related_models(model_table_map):
            models_list.append(dict_for_model(model))
        return self.sort_filter_models(models_list)

    @api.model
    def get_join_nodes(self, field_data, new_field):
        """ Return list of field dicts of join nodes

            Return all possible join nodes to add new_field to the query
            containing model_ids.
        """
        def _get_model_table_map(field_data):
            table_map = defaultdict(list)
            for data in field_data:
                table_map[data['model_id']].append(data['table_alias'])
            return table_map

        def _get_join_nodes_dict(model_table_map, new_field):
            join_nodes = []
            for alias in model_table_map[new_field['model_id']]:
                join_nodes.append({'table_alias': alias})

            for field in self.get_model_list(model_table_map):
                if new_field['model'] == field['relation']:
                    join_nodes.append(field)

            for field in self.get_relation_list(model_table_map):
                if new_field['model_id'] == field['model_id']:
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

        self = self.with_context(lang=self.env.user.lang)
        model_table_map = _get_model_table_map(field_data)
        keys = [(field['table_alias'], field['id'])
                for field in field_data if field.get('join_node', -1) != -1]
        join_nodes = _get_join_nodes_dict(model_table_map, new_field)
        join_nodes = remove_duplicate_nodes(join_nodes)

        return list(filter(
            lambda x: 'id' not in x or
                      (x['table_alias'], x['id']) not in keys, join_nodes))

    @api.model
    def get_fields(self, model_id):
        self = self.with_context(lang=self.env.user.lang)
        domain = [
            ('model_id', '=', model_id),
            ('store', '=', True),
            ('name', 'not in', models.MAGIC_COLUMNS),
            ('ttype', 'not in', NO_BI_TTYPES)
        ]
        fields_dict = []
        for field in self.env['ir.model.fields'].sudo().search(domain):
            fields_dict.append({
                'id': field.id,
                'model_id': model_id,
                'name': field.name,
                'description': field.field_description,
                'type': field.ttype,
                'model': field.model,
            })
        return sorted(
            fields_dict,
            key=lambda x: x['description'],
            reverse=True
        )

    @api.model
    def create(self, vals):
        if self.env.context and self.env.context.get('bve'):
            vals['state'] = 'base'
        res = super().create(vals)

        # this sql update is necessary since a write method here would
        # be not working (an orm constraint is restricting the modification
        # of the state field while updating ir.model)
        q = "UPDATE ir_model SET state = 'manual' WHERE id = %s"
        self.env.cr.execute(q, (res.id, ))

        # # update registry
        if self.env.context.get('bve'):
            # setup models; this reloads custom models in registry
            self.pool.setup_models(self._cr)

            # signal that registry has changed
            registry(self.env.cr.dbname).signal_changes()

        return res
