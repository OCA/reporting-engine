import base64
from collections import defaultdict

import polars as pl

from odoo import exceptions, fields, models

MODULE = __name__[12 : __name__.index(".", 13)]


class SheetDataframeTransient(models.TransientModel):
    _name = "sheet.dataframe.transient"
    _description = "Create polars dataframe from spreadsheet like file"

    config_id = fields.Many2one(comodel_name="file.config", required=True)
    partner_id = fields.Many2one(comodel_name="res.partner")
    comment = fields.Html(readonly=True)
    sample = fields.Html(readonly=True)
    filename = fields.Char()
    file = fields.Binary(attachment=False)

    def create(self, vals):
        res = super().create(vals)
        if res.config_id and res.file:
            res._pre_process()
        return res

    def _pre_process(self):
        self.ensure_one()
        attribs = {}
        df, specific_recs = self._get_base_info()
        partner, specific_names = self._guess_partner(df, specific_recs)
        if partner:
            self.partner_id = partner.id
            map_cols = self._get_map_cols(df, specific_recs, partner)
            # TODO improve miss_col
            # attribs["miss_col"] = self._check_missing_cols(df, map_cols)
            df = self._rename_df_columns(df, map_cols)
            attribs.update(self._check_missing_values(df))
        self.sample = f"<pre>\n{self._2html(df)}\n</pre>"
        self.comment = "<pre>%s</pre>" % (" ".join(
            [
                f'<div id="{self._slug_me(key)}"><div>{key}</div>{self._2html(data)}</div>'
                for key, data in attribs.items()
            ])
        )
        self._reload()

    def _get_base_info(self):
        df = pl.read_excel(source=base64.b64decode(self.file)).with_row_index(
            name="N°", offset=1
        )
        specific_recs = self.config_id.field_match_ids.filtered(
            lambda s, df_cols=df.columns: s.matching_column in df_cols
        )
        return df, specific_recs

    def _get_map_cols(self, df, specific_recs, partner):
        return {
            x.matching_column: x.field_id.name
            for x in specific_recs.filtered(
                lambda s, part=partner: s.partner_id == part
            )
        }

    def _rename_df_columns(self, df, map_cols):
        new_cols = {x: map_cols.get(x) for x in df.columns if x in map_cols}
        return df.rename(new_cols)

    def _check_missing_values(self, df):
        requireds = self.config_id.field_ids.filtered(
            lambda s: s.required and s.field_id.name in df.columns
        ).mapped("field_id.name")
        dico = {}
        for req in requireds:
            res = df.filter(pl.col(req).is_null())
            if len(res):
                dico[f"Missing '{req}' values"] = res
        return dico

    def _check_missing_cols(self, df, map_cols):
        file_techn_name_cols = [map_cols.get(x, x) for x in df.columns]
        required = self.config_id.field_ids.filtered(lambda s: s.required).mapped(
            "field_id.name"
        )
        missing = [x for x in required if x not in file_techn_name_cols]
        return missing or ""

    def _guess_partner(self, df, specific_recs):
        cols_by_part = defaultdict(list)
        for line in specific_recs:
            cols_by_part[line.partner_id].append(line.matching_column)
        if len(cols_by_part) > 1:
            self._manage_several_partners(cols_by_part.keys())
        if cols_by_part:
            # only custom columns of first partner
            partner = list(cols_by_part.keys())[0]
            return partner, cols_by_part[partner]
        # Not supported case
        return False, []

    def process(self):
        """
        - apply skip to record when required not respected
        """

    def _2html(self, df):
        if isinstance(df, pl.dataframe.frame.DataFrame):
            return str(df.__repr__)[:-1].replace("\n", "<br />").replace("null", "    ")
        return df

    def _reload(self):
        action = self.env.ref(
            f"{MODULE}.sheet_dataframe_transient_action"
        )._get_action_dict()
        action["res_id"] = self.id
        return action

    def _manage_several_partners(self, partners):
        raise exceptions.UserError(
            f"Several partners found {partners.mapped('name')}:\n\nNot implemented case"
        )

    def _slug_me(self, string):
        string = string.replace("'", "").replace(" ", "-").lower()
        return string
