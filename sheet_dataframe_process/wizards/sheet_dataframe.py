import base64
from collections import defaultdict

import polars as pl

from odoo import _, exceptions, fields, models

MODULE = __name__[12 : __name__.index(".", 13)]


class SheetDataframeTransient(models.TransientModel):
    _name = "sheet.dataframe.transient"
    _description = "Create polars dataframe from spreadsheet like file"

    config_id = fields.Many2one(comodel_name="file.config", required=True)
    partner_id = fields.Many2one(comodel_name="res.partner")
    comment = fields.Char()
    sample = fields.Html(readonly=True)
    filename = fields.Char()
    file = fields.Binary(attachment=False)
    missing_cols = fields.Char()

    def create(self, vals):
        res = super().create(vals)
        if res.config_id and res.file:
            res._pre_process()
        return res

    def _pre_process(self):
        self.ensure_one()
        comment = ""
        df = pl.read_excel(source=base64.b64decode(self.file))
        spe_records = self.config_id.field_match_ids.filtered(
            lambda s, df_cols=df.columns: s.matching_column in df_cols
        )
        partner, specific_names = self._guess_partner(df, spe_records)
        if partner:
            self.partner_id = partner.id
            self.missing_cols = self._check_missing_cols(df, spe_records, partner)
        if self.missing_cols:
            comment += _(f"\nMissing columns: {self.missing_cols}")
        self._dataframe2html(df)
        self.comment = comment
        self._reload()

    def process(self):
        """
        - apply skip to record when required not respected
        """

    def _check_missing_value(self, df):
        df.rename({"foo": "apple"})

    def _check_missing_cols(self, df, spe_records, partner):
        map_cols = {
            x.matching_column: x.field_id.name
            for x in spe_records.filtered(lambda s, part=partner: s.partner_id == part)
        }
        file_techn_name_cols = [map_cols.get(x, x) for x in df.columns]
        required = self.config_id.field_ids.filtered(lambda s: s.required).mapped(
            "field_id.name"
        )
        missing = [x for x in required if x not in file_techn_name_cols]
        return missing or ""

    def _guess_partner(self, df, spe_records):
        cols_by_part = defaultdict(list)
        for line in spe_records:
            cols_by_part[line.partner_id].append(line.matching_column)
        if len(cols_by_part) > 1:
            self._manage_several_partners(cols_by_part.keys())
        if cols_by_part:
            # only custom columns of first partner
            partner = list(cols_by_part.keys())[0]
            return partner, cols_by_part[partner]
        # Not supported case
        return False, []

    def _dataframe2html(self, df):
        sample = str(df.__repr__)[:-1].replace("\n", "<br />")
        self.sample = f"<pre>\n{sample}\n</pre>"

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
