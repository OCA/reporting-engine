import base64

import polars as pl
from lxml import etree, html

from odoo import fields, models

MODULE = __name__[12 : __name__.index(".", 13)]


class DfProcessWiz(models.TransientModel):
    _name = "df.process.wiz"
    _description = "Process Polars dataframe"

    dataframe_id = fields.Many2one(comodel_name="dataframe", required=True)
    comment = fields.Html(readonly=True)
    sample = fields.Html(readonly=True)
    filename = fields.Char()
    file = fields.Binary(attachment=False)
    df_source_id = fields.Many2one(comodel_name="df.source")

    def create(self, vals):
        res = super().create(vals)
        if res.dataframe_id and res.file:
            res._pre_process()
        return res

    def _pre_process(self):
        self.ensure_one()
        attribs = {}
        df = self._get_dataframe()
        requireds = self._get_requireds(df)
        if requireds:
            missing_columns = self._check_missing_cols(df, requireds)
            if missing_columns:
                attribs["Missing Columns"] = missing_columns
            requireds = [x for x in requireds if x not in missing_columns]
            attribs.update(self._check_missing_values(df, requireds))
        self.sample = f"{self._2html(df)}"
        source = self.df_source_id
        if source and source.rename:
            renamed_df, rdf = self._rename_df_columns(df)
            if renamed_df:
                attribs["Renamed Columns"] = rdf
        self._pre_process_hook(df, attribs)
        comment = "\n".join(
            [
                f'<div id="{self._slug_me(key)}"><div>{key}:</div>'
                f'<div id="{self._slug_me(key)}-data">{self._2html(data)}</div></div>'
                for key, data in attribs.items()
            ]
        )
        if comment:
            self.comment = etree.tostring(
                html.fromstring(comment), encoding="unicode", pretty_print=True
            )
        self._reload()

    def _pre_process_hook(self, df, attribs):
        "Inherit for your own behavior"
        self.ensure_one()

    def _get_dataframe(self):
        return pl.read_excel(source=base64.b64decode(self.file)).with_row_index(
            name="N°", offset=1
        )

    def _check_missing_values(self, df, requireds):
        dico = {}
        for req in requireds:
            res = df.filter(pl.col(req).is_null())
            if len(res):
                dico[f"Missing values in '{req}'"] = res
        return dico

    def _check_missing_cols(self, df, requireds):
        missing = [x for x in requireds if x not in df.columns]
        return missing or ""

    def _get_requireds(self, df):
        requireds = self.dataframe_id.field_ids.filtered(
            lambda s, df=df: s.required and s.name or s.field_id.name in df.columns
        )
        return [x.name or x.field_id.name for x in requireds]

    def process(self):
        """
        - apply skip to record when required not respected
        """

    def _rename_df_columns(self, df):
        map_cols = {
            x.name: x.renamed
            for x in self.dataframe_id.field_ids.filtered(lambda s: s.renamed)
        }
        new_cols = {x: map_cols.get(x) for x in df.columns if x in map_cols}
        if new_cols:
            return True, df.rename(new_cols)
        return False, False

    def _2html(self, df):
        if isinstance(df, pl.dataframe.frame.DataFrame):
            string = (
                str(df.__repr__)[:-1].replace("\n", "<br />").replace("null", "    ")
            )
            return f"\n\t\t<pre>{string}\n\t\t</pre>"
        return df

    def _reload(self):
        action = self.env.ref(f"{MODULE}.df_process_wiz_action")._get_action_dict()
        action["res_id"] = self.id
        return action

    def _slug_me(self, string):
        string = string.replace("'", "").replace(" ", "-").lower()
        return string
