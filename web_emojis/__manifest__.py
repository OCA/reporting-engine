# Copyright 2026 Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

# workaround module for:
# https://github.com/wkhtmltopdf/wkhtmltopdf/issues/2913
# wkhtmltopdf supports some emojis in black & white only, and color
# emojis aren't supported at all.
# For example, ⚠️ would be rendered as simple line drawing in pdf,
# and not as a colorful yellow warning sign.
# Meanwhile, 🇫🇷 would render as missing glyphs instead of the French flag.
# So it's not perfect as true emoji support would mean that copy-paste
# would work while this is not the case with this workaround.


{
    "name": "Web Emojis",
    "summary": """
Replaces emojis with Twemoji images in PDF reports.

Emojis cannot be rendered by wkhtmltopdf. This module automatically converts
them to img tags pointing to Twemoji images before PDF generation.
    """,
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "Lambdao, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/reporting-engine",
    "category": "Technical",
    "depends": ["base"],
    "external_dependencies": {"python": ["emoji_data_python", "twemoji_api"]},
    "demo": ["report/demo_report.xml"],
    "installable": True,
}
