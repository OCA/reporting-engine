# Copyright 2022 Sunflower IT <https://www.sunflowerweb.nl>.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).

{
    "name": "Choose report page orientation",
    "version": "15.0.1.0.0",
    "author": "Sunflower IT",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "category": "Reporting",
    "summary": "Allows for individual pages of reports to have different page "
    "orientation",
    "depends": ["base"],
    "data": [
        "views/views.xml",
    ],
    "external_dependencies": {"python": ["PyPDF2"]},
    "demo": ["demo/report_page_orientation_demo.xml"],
    "application": False,
}
