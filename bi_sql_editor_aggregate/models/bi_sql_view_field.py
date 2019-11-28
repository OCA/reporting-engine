# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class BiSQLViewField(models.Model):
    _inherit = 'bi.sql.view.field'

    _GROUP_OPERATOR_SELECTION = [
        ('sum', 'Sum'),
        ('avg', 'Average'),
        ('min', 'Minimum'),
        ('max', 'Maximum'),
    ]

    _GRAPH_TYPE_SELECTION = [
        ('col', 'Column'),
        ('row', 'Row'),
        ('measure', 'Measure'),
    ]

    group_operator = fields.Selection(
        string='Group Operator', selection=_GROUP_OPERATOR_SELECTION,
        help="By default, Odoo will sum the values when grouping. If you wish"
        " to alter the behaviour, choose an alternate Group Operator")
