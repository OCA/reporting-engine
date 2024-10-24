# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Polars Database Process",
    "version": "18.0.1.0.0",
    "summary": "Allow to create a Polars dataframe from database query and "
    "check it and process it according to rules",
    "category": "Reporting",
    "license": "AGPL-3",
    "author": "Akretion, Odoo Community Association (OCA)",
    "development_status": "Alpha",
    "website": "https://github.com/OCA/reporting-engine",
    "maintainers": ["bealdav"],
    "depends": [
        "polars_process",
    ],
    "external_dependencies": {
        "python": [
            "connectorx",
        ]
    },
    "data": [
        "data/demo.xml",
        "wizards/df_process.xml",
        "views/dataframe.xml",
        "views/df_field.xml",
        "views/df_source.xml",
    ],
    "installable": True,
}
