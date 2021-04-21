# Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from collections import defaultdict

from odoo import api, models

NO_BI_MODELS = ["fetchmail.server"]

NO_BI_TTYPES = ["many2many", "one2many", "html", "binary", "reference"]


def dict_for_field(field):
    return {
        "id": field.id,
        "name": field.name,
        "description": field.field_description,
        "type": field.ttype,
        "relation": field.relation,
        "custom": False,
        "model_id": field.model_id.id,
        "model": field.model_id.model,
        "model_name": field.model_id.name,
    }


def dict_for_model(model):
    return {"id": model.id, "name": model.name, "model": model.model}


class IrModel(models.Model):
    _inherit = "ir.model"

    @api.model
    def _filter_bi_models(self, model):
        def _check_name(model_model):
            if model_model in NO_BI_MODELS:
                return 1
            return 0

        def _check_startswith(model_model):
            if (
                model_model.startswith("workflow")
                or model_model.startswith("ir.")
                or model_model.startswith("base_")
            ):
                return 1
            return 0

        def _check_contains(model_model):
            if (
                "mail" in model_model
                or "report" in model_model
                or "edi." in model_model
            ):
                return 1
            return 0

        def _check_unknown(model_name):
            if model_name == "Unknown" or "." in model_name:
                return 1
            return 0

        model_model = model["model"]
        model_name = model["name"]
        count_check = 0
        count_check += _check_name(model_model)
        count_check += _check_startswith(model_model)
        count_check += _check_contains(model_model)
        count_check += _check_unknown(model_name)
        if not count_check:
            return self.env["ir.model.access"].check(model["model"], "read", False)
        return False

    def get_model_list(self, model_table_map):
        if not model_table_map:
            return []
        domain = [
            ("model_id", "in", list(model_table_map.keys())),
            ("store", "=", True),
            ("ttype", "=", "many2one"),
        ]
        fields = self.env["ir.model.fields"].sudo().search(domain)
        model_list = []
        for field in fields:
            for table_alias in model_table_map[field.model_id.id]:
                model_list.append(
                    dict(
                        dict_for_field(field),
                        table_alias=table_alias,
                        join_node=-1,
                    )
                )
        return model_list

    def get_relation_list(self, model_table_map):
        if not model_table_map:
            return []
        model_names = {}
        for model in self.sudo().browse(model_table_map.keys()):
            model_names.update({model.model: model.id})

        domain = [
            ("relation", "in", list(model_names.keys())),
            ("store", "=", True),
            ("ttype", "=", "many2one"),
        ]
        fields = self.env["ir.model.fields"].sudo().search(domain)
        relation_list = []
        for field in fields:
            model_id = model_names[field.relation]
            for join_node in model_table_map[model_id]:
                relation_list.append(
                    dict(dict_for_field(field), join_node=join_node, table_alias=-1)
                )
        return relation_list

    @api.model
    def _get_related_models_domain(self, model_table_map):
        domain = [("transient", "=", False)]
        if model_table_map:
            model_list = self.get_model_list(model_table_map)
            relation_list = self.get_relation_list(model_table_map)
            model_ids = [f["model_id"] for f in relation_list + model_list]
            model_ids += list(model_table_map.keys())
            relations = [f["relation"] for f in model_list]
            domain += ["|", ("id", "in", model_ids), ("model", "in", relations)]
        return domain

    @api.model
    def get_related_models(self, model_table_map):
        """Return list of model dicts for all models that can be
        joined with the already selected models.
        """
        domain = self._get_related_models_domain(model_table_map)
        return self.sudo().search(domain, order="name asc")

    @api.model
    def get_models(self, table_model_map=None):
        """Return list of model dicts for all available models."""
        self = self.with_context(lang=self.env.user.lang)
        model_table_map = defaultdict(list)
        for k, v in (table_model_map or {}).items():
            model_table_map[v].append(k)

        models = self.get_related_models(model_table_map)

        # filter out abstract models (they do not have DB tables)
        non_abstract_models = self.env.registry.models.keys()
        models = models.filtered(lambda m: m.model in non_abstract_models)

        return list(map(dict_for_model, models))

    @api.model
    def get_join_nodes(self, field_data, new_field):
        """Return list of field dicts of join nodes

        Return all possible join nodes to add new_field to the query
        containing model_ids.
        """

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

        keys = []
        model_table_map = defaultdict(list)
        for field in field_data:
            model_table_map[field["model_id"]].append(field["table_alias"])
            if field.get("join_node", -1) != -1:
                keys.append((field["table_alias"], field["id"]))

        # nodes in current model
        existing_aliases = model_table_map[new_field["model_id"]]
        join_nodes = [{"table_alias": alias} for alias in existing_aliases]

        # nodes in past selected models
        for field in self.get_model_list(model_table_map):
            if new_field["model"] == field["relation"]:
                if (field["table_alias"], field["id"]) not in keys:
                    join_nodes.append(field)

        # nodes in new model
        for field in self.get_relation_list(model_table_map):
            if new_field["model_id"] == field["model_id"]:
                if (field["table_alias"], field["id"]) not in keys:
                    join_nodes.append(field)

        return remove_duplicate_nodes(join_nodes)

    @api.model
    def get_fields(self, model_id):
        self = self.with_context(lang=self.env.user.lang)

        fields = (
            self.env["ir.model.fields"]
            .sudo()
            .search(
                [
                    ("model_id", "=", model_id),
                    ("store", "=", True),
                    ("name", "not in", models.MAGIC_COLUMNS),
                    ("ttype", "not in", NO_BI_TTYPES),
                ],
                order="field_description desc",
            )
        )
        fields_dict = list(map(dict_for_field, fields))
        return fields_dict
