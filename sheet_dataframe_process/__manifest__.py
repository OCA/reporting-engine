# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sheet Dataframe Process",
    "version": "18.0.1.0.0",
    "category": "Reporting",
    "license": "AGPL-3",
    "summary": "Allow to create a Polars dataframe from a sheet file and "
    "process it according to rules",
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
        "security/ir.model.access.xml",
        "wizards/sheet_dataframe.xml",
        "views/file_config.xml",
        "views/file_field.xml",
        "views/file_partner_field.xml",
        # "views/file_config_field.xml",
        "views/test_polars_file.xml",
        "views/menu.xml",
        "data/action.xml",
        "data/demo.xml",
    ],
    "installable": True,
}
