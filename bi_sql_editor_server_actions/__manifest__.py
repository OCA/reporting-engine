# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "BI SQL Editor Server Actions",
    "summary": "Add server actions on BI Views builder module",
    "version": "13.0.1.0.1",
    "license": "AGPL-3",
    "category": "Reporting",
    "author": "GRAP,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": ["base", "bi_sql_editor"],
    "data": ["views/ir_actions_server_view.xml", "views/view_bi_sql_view.xml"],
    "demo": [],
    "maintainers": ["vnahaulogy"],
    "installable": True,
}
