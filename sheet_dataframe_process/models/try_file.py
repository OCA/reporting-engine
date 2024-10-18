import base64
from pathlib import Path

from odoo import fields, models
from odoo.modules.module import get_module_path


class TestPolarsFile(models.Model):
    _name = "try.file"
    _description = "Example files to ensure your configuration match with cases"

    config_id = fields.Many2one(
        comodel_name="file.config", required=True, ondelete="cascade", readonly=True
    )
    name = fields.Char()
    template = fields.Binary(string="Fichier", attachment=False)

    def _populate(self):
        def create_attach(myfile, addon, idstring, relative_path):
            with open(myfile, "rb") as f:
                vals = {
                    "config_id": self.env.ref(idstring).id,
                    "name": f.name[f.name.find(addon) :],
                }
                self.env[self._name].sudo().create(vals)

        self.env[self._name].search([("template", "=", False)]).unlink()
        paths = self._get_test_file_paths()
        for addon, data in paths.items():
            relative_path = data["relative_path"]
            idstring = f"{addon}.{data['xmlid']}"
            if self.env.ref(idstring):
                mpath = Path(get_module_path(addon)) / relative_path
                for mfile in tuple(mpath.iterdir()):
                    create_attach(mfile, addon, idstring, relative_path)
        action = self.env.ref(
            "sheet_dataframe_process.try_file_action"
        )._get_action_dict()
        return action

    def try_import(self):
        self.ensure_one()
        transient = self.env["sheet.dataframe.transient"].create(
            {
                "filename": self.name,
                "file": self._get_file(),
                "config_id": self.config_id.id,
            }
        )
        action = self.env.ref(
            "sheet_dataframe_process.sheet_dataframe_transient_action"
        )._get_action_dict()
        action["res_id"] = transient.id
        return action

    def _get_file(self):
        # TODO Clean
        if self.template:
            return self.template
        module = self.name[: self.name.find("/")]
        relative = self._get_test_file_paths().get(module)
        relative = relative and relative.get("relative_path")
        if relative:
            path = Path(get_module_path(module))
            path = path / relative / self.name[self.name.rfind("/") + 1 :]
            # myfile = path / self.name
            with open(path, "rb") as f:
                return base64.b64encode(f.read())

    def _get_test_file_paths(self):
        """
        You may override if you want populate files in your module
        returns:
        {"module_name": {
            "relative_path": "tests/files",
            "xmlid": "file_config_xml_id"}
            }
        }
        """
        return {
            "sheet_dataframe_process": {
                "relative_path": "tests/files",
                "xmlid": "file_config_contact",
            }
        }
