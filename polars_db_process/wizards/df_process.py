from odoo import _, exceptions, models

MODULE = __name__[12 : __name__.index(".", 13)]


class DfProcessWiz(models.TransientModel):
    _inherit = "df.process.wiz"

    def _pre_process(self):
        res = super()._pre_process()
        if not self.file:
            self._pre_process_sql()
        return res

    def _pre_process_sql(self):
        raise exceptions.ValidationError(_("to be continued"))
