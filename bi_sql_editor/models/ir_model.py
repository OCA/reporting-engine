import logging

from odoo import models
from odoo.tools import sql

# Same logger as core's ir_model.py, so the log for genuinely unexpected
# non-regular tables (i.e. not ours) still appears under its usual name.
_logger = logging.getLogger("odoo.addons.base.models.ir_model")


class IrModel(models.Model):
    _inherit = "ir.model"

    def _get_bi_sql_view_model_names(self):
        """Names of the models backed by a bi_sql_editor SQL/materialized view.

        Being backed by a view is expected for these, so
        ``_add_manual_models`` should not warn about it (see
        OCA/reporting-engine#1120).
        """
        self.env.cr.execute(
            "SELECT model_name FROM bi_sql_view WHERE model_id IS NOT NULL"
        )
        return {row[0] for row in self.env.cr.fetchall()}

    def _add_manual_models(self):
        # Full copy of ir.model._add_manual_models() (odoo/addons/base/models
        # /ir_model.py), with the "disabling automatic schema management"
        # log guarded below. Keep in sync with core on upgrade.
        # clean up registry first
        for name, Model in list(self.pool.items()):
            if Model._custom:
                del self.pool.models[name]
                # remove the model's name from its parents' _inherit_children
                for Parent in Model.__bases__:
                    if hasattr(Parent, "pool"):
                        Parent._inherit_children.discard(name)

        known_view_models = self._get_bi_sql_view_model_names()  # the real change

        # add manual models
        cr = self.env.cr
        # we cannot use self._fields to determine translated fields, as it
        # has not been set up yet
        cr.execute(
            "SELECT *, name->>'en_US' AS name FROM ir_model WHERE state = 'manual'"
        )
        for model_data in cr.dictfetchall():
            model_class = self._instanciate(model_data)
            Model = model_class._build_model(self.pool, cr)
            kind = sql.table_kind(cr, Model._table)
            if kind not in (sql.TableKind.Regular, None):
                if Model._name not in known_view_models:  # the real change
                    _logger.info(
                        "Model %r is backed by table %r which is not a regular"
                        " table (%r), disabling automatic schema management",
                        Model._name,
                        Model._table,
                        kind,
                    )
                Model._auto = False
                cr.execute(
                    """
                    SELECT a.attname
                      FROM pg_attribute a
                      JOIN pg_class t
                        ON a.attrelid = t.oid
                       AND t.relname = %s
                     WHERE a.attnum > 0 -- skip system columns
                    """,
                    [Model._table],
                )
                columns = {colinfo[0] for colinfo in cr.fetchall()}
                Model._log_access = set(models.LOG_ACCESS_COLUMNS) <= columns


class IrModelFields(models.Model):
    _inherit = "ir.model.fields"

    def _add_manual_fields(self, model):
        res = super()._add_manual_fields(model)
        self.env["bi.sql.view"].check_manual_fields(model)
        return res
