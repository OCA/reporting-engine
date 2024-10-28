from pathlib import Path

from odoo import fields, models
from odoo.modules.module import get_module_path
from odoo.tools.safe_eval import safe_eval

MODULE = __name__[12 : __name__.index(".", 13)]

HELP = """Supported files: .xlsx and .sql
Sql files may contains a comment on first line
to be mapped automatically with dataframe, i.e:\n
-- {'model_id': 'product.product', 'db_id': mydb}
-- {'code': 'my_delivery_address', 'db_id': mydb}
"""


class DfSource(models.Model):
    _inherit = "df.source"

    name = fields.Char(help=HELP)
    query = fields.Char()
    # TODO : -> db_config_id
    db_id = fields.Many2one(comodel_name="db.config", help="Database")

    def _file_hook(self, file):
        "Map sql file with the right Odoo model via dataframe and the right db.config"
        vals = super()._file_hook(file)
        if ".sql" in file:
            # TODO: improve
            content = self._get_file(file).decode("utf-8")
            contents = content.split("\n")
            if contents:
                # we only detect first line
                metadata = safe_eval(contents[0].replace("--", ""))
                model_name = metadata.get("model")
                model = self.env["ir.model"].search([("model", "=", model_name)])
                if model_name:
                    # we don't want to use these dataframes
                    dataframes = (
                        self.env["df.source"]
                        .search([])
                        .filtered(lambda s: not s.db_id)
                        .mapped("dataframe_id")
                    )
                    dataframe = self.env["dataframe"].search(
                        [
                            ("id", "not in", dataframes.ids),
                            ("model_id", "=", model_name),
                        ]
                    )
                    if dataframe:
                        # TODO use first
                        vals["dataframe_id"] = dataframe[0].id
                        db_config = self.env["db.config"].search(
                            [("name", "ilike", metadata.get("db_id"))]
                        )
                        vals["db_id"] = db_config and db_config[0].id or False
                    else:
                        df = self.env["dataframe"].create(
                            {"code": model.name, "model_id": model and model[0].id}
                        )
                        vals["dataframe_id"] = df.id
            vals["query"] = content
        return vals

    def _populate(self):
        chinook = self.env.ref(f"{MODULE}.sqlite_chinook")
        if chinook:
            # Demo behavior only
            path = Path(get_module_path(MODULE)) / "data/chinook.sqlite"
            chinook.string_connexion = f"sqlite://{str(path)}"
        return super()._populate()

    def _get_test_file_paths(self):
        res = super()._get_test_file_paths()
        res.update(
            {
                "polars_db_process": {
                    "relative_path": "data/files",
                    "xmlid": "polars_db_process.contact_chinook",
                }
            }
        )
        return res
