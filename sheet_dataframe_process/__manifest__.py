{
    "name": "Spreadsheet Import Configurable",
    "version": "18.0.1.0.0",
    "author": "Akretion",
    "license": "GPL-3",
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
        # "wizards/sheet_dataframe.xml",
        "views/file_config.xml",
        "views/file_field.xml",
        "views/file_partner_field.xml",
        # "views/file_config_field.xml",
        # "views/test_file.xml",
        # "data/action.xml",
        # "data/misc.xml",
        "data/demo.xml",
    ],
    "installable": True,
}
