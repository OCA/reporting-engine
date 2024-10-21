# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sheet Dataframe Process",
    "version": "18.0.1.0.0",
    "summary": "Allow to create a Polars dataframe from a sheet file and "
    "process it according to rules",
    "category": "Reporting",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/reporting-engine",
    "maintainers": ["bealdav"],
    "depends": [
        "contacts",
    ],
    "external_dependencies": {
        "python": [
            "polars",
            "fastexcel",
        ]
    },
    "data": [
        "data/action.xml",
        "data/demo.xml",
        "security/ir.model.access.xml",
        "wizards/sheet_dataframe.xml",
        "views/file_config.xml",
        "views/file_field.xml",
        "views/file_partner_field.xml",
        "views/try_file.xml",
        "views/menu.xml",
    ],
    "installable": True,
}
