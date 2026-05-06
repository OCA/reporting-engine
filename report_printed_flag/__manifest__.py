{
    "name": "Report Printed Flag",
    "summary": "Configure reports that mark records as printed",
    "version": "17.0.1.0.0",
    "category": "Tools",
    "license": "AGPL-3",
    "author": "Binhex Systems Solutions S.L, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "depends": [
        "base",
        "web",
    ],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "views/report_printed_config_views.xml",
        "views/report_printed_log_views.xml",
        "views/menu_views.xml",
    ],
    "installable": True,
    "development_status": "Alpha",
}
