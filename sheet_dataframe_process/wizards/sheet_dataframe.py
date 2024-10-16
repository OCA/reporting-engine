import base64

import polars as pl

from odoo import fields, models

MODULE = __name__[12 : __name__.index(".", 13)]


class SheetDataframeTransient(models.TransientModel):
    _name = "sheet.dataframe.transient"
    _description = "Create polars dataframe from spreadsheet like file"

    config_id = fields.Many2one(comodel_name="file.config", required=True)
    sample = fields.Html(readonly=True)
    filename = fields.Char()
    file = fields.Binary(attachment=False)

    def create(self, vals):
        res = super().create(vals)
        if res.config_id and res.file:
            res.apply()
        return res

    def apply(self):
        self.ensure_one()
        file = base64.b64decode(self.file)
        df = pl.read_excel(source=file)
        sample = str(df.__repr__).replace("\n", "<br />").replace("┘&gt;", "")
        self.sample = f"<html><pre>\n{sample}\n</pre></html>"
        action = self.env.ref(
            f"{MODULE}.sheet_dataframe_transient_action"
        )._get_action_dict()
        action["res_id"] = self.id
        return action
