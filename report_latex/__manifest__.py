# Copyright 2025 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

{
    "name": "LaTeX reports",
    "category": "Reporting",
    "version": "18.0.1.0.0",
    "author": "Lambdao, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "license": "AGPL-3",
    "summary": """Create LaTeX reports.""",
    "depends": ["web", "mail"],
    "external_dependencies": {
        "python": ["jinja2"],
        "deb": ["texlive", "texlive-latex-extra"],  # pdflatex, latexpand
    },
    "installable": True,
    "auto_install": False,
    "data": [
        "security/ir.model.access.csv",
        "views/ir_actions_report.xml",
        "views/latex_template.xml",
        "views/latex_source.xml",
        "views/menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            "report_latex/static/src/js/latexactionservice.esm.js",
        ],
        "web._assets_core": [
            "report_latex/static/src/js/code_editor.esm.js",
        ],
        "web.ace_lib": [
            "report_latex/static/lib/ace/mode-latex.js",
        ],
    },
    "demo": [
        "demo/report_attachments.xml",
        "demo/report_latex.xml",
    ],
}
