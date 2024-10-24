from odoo import models

MODULE = __name__[12 : __name__.index(".", 13)]


class DfProcessWiz(models.TransientModel):
    _inherit = "df.process.wiz"
