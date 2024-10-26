import base64
from pathlib import Path

from odoo import _, fields, models
from odoo.modules.module import get_module_path


class DfSource(models.Model):
    _name = "df.source"
    _description = "Dataframe data source"

    dataframe_id = fields.Many2one(
        comodel_name="dataframe", required=True, ondelete="cascade"
    )
    name = fields.Char()
    sequence = fields.Integer()
    rename = fields.Boolean(help="Display renamed Dataframe in wizard")
    template = fields.Binary(string="File", attachment=False)
    readonly = fields.Boolean(help="Imported records from module are readonly created")

    def _populate(self):
        def create_attach(myfile, addon, idstring, relative_path):
            with open(myfile, "rb") as f:
                name = f.name[f.name.find(addon) :]
                vals = {
                    "dataframe_id": self.env.ref(idstring).id,
                    "name": name,
                    "readonly": True,
                    "rename": True,
                }
                if ".sql" in name:
                    vals["query"] = self._get_file(name)
                self.env[self._name].sudo().create(vals)

        self.env[self._name].search([("template", "=", False)]).unlink()
        paths = self._get_test_file_paths()
        for addon, data in paths.items():
            relative_path = data["relative_path"]
            idstring = data["xmlid"]
            if self.env.ref(idstring):
                mpath = Path(get_module_path(addon)) / relative_path
                for mfile in tuple(mpath.iterdir()):
                    create_attach(mfile, addon, idstring, relative_path)
        action = self.env.ref("polars_process.df_source_action")._get_action_dict()
        return action

    def start(self):
        self.ensure_one()
        vals = {
            "filename": self.name,
            "df_source_id": self.id,
            "dataframe_id": self.dataframe_id.id,
            "file": base64.b64encode(self._get_file()),
        }
        transient = self.env["df.process.wiz"].create(vals)
        action = self.env.ref("polars_process.df_process_wiz_action")._get_action_dict()
        action["res_id"] = transient.id
        return action

    def _get_file(self, name=None):
        # TODO Clean
        if self.template:
            return self.template
        name = self.name or name
        module = name[: name.find("/")]
        relative = self._get_test_file_paths().get(module)
        relative = relative and relative.get("relative_path")
        if relative:
            path = Path(get_module_path(module))
            path = path / relative / name[name.rfind("/") + 1 :]
            with open(path, "rb") as f:
                return f.read()

    def _get_test_file_paths(self):
        """
        You may override if you want populate files in your module
        returns:
        {"module_name": {
            "relative_path": "tests/files",
            "xmlid": "dataframe_xml_id"}
            }
        }
        """
        return {
            "polars_process": {
                "relative_path": "tests/files",
                "xmlid": "polars_process.dataframe_contact",
            }
        }

    def ui_form(self):
        self.ensure_one()
        return {
            "name": _("Dataframe source"),
            "res_model": self._name,
            "view_mode": "form",
            "res_id": self.id,
            "type": "ir.actions.act_window",
            "target": "current",
        }
