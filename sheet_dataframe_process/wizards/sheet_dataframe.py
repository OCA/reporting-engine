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
            res._pre_process()
        return res

    def process(self):
        """
        - apply skip to record when required not respected
        """

    def _pre_process(self):
        self.ensure_one()
        df = pl.read_excel(source=base64.b64decode(self.file))
        self.sample = self._dataframe2html(df)
        self._reload()

    def _dataframe2html(self, df):
        sample = str(df.__repr__).replace("\n", "<br />").replace("┘&gt;", "")
        return f"<html><pre>\n{sample}\n</pre></html>"

    def _reload(self):
        action = self.env.ref(
            f"{MODULE}.sheet_dataframe_transient_action"
        )._get_action_dict()
        action["res_id"] = self.id
        return action
