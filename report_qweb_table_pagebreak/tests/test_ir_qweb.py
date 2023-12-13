from lxml import html

from odoo.tests.common import TransactionCase

from odoo.addons.report_qweb_table_pagebreak.models.ir_qweb import StyleParser


class TestIrQwebTableTrPageBreak(TransactionCase):
    def setUp(self):
        super().setUp()
        self.maxDiff = None

    def normalized(self, html_str):
        return (
            html.tostring(
                html.document_fromstring(
                    " ".join(
                        [
                            s
                            for s in html_str.replace("><", "> <")
                            .replace("\t", " ")
                            .replace("\n", " ")
                            .split(" ")
                            if s.strip()
                        ]
                    ).replace("<", "\n<")
                ),
                pretty_print=True,
            )
            .decode("utf-8")
            .replace("&gt;", ">")
            .replace("&lt;", "<")
        )

    def assertHtml(self, first, second):
        self.assertEqual(self.normalized(first), self.normalized(second))

    def test_render_without_data_page_break(self):
        val = {
            "name": "ABC",
            "address": "Adresse",
            "country_id": self.env.user.partner_id.country_id,
            "fields": [
                "name",
                "address",
            ],
            "object": self.env.user.partner_id,
            "options": {},
        }
        self.assertHtml(
            self.env["ir.qweb"]._render("base.contact", values=val).decode("utf-8"),
            """<address class="mb-0"
                    itemscope="itemscope"
                    itemtype="http://schema.org/Organization">
                <div>
                    <span itemprop="name">ABC</span>
                </div>
                <div itemprop="address"
                     itemscope="itemscope"
                     itemtype="http://schema.org/PostalAddress">
                    <div class="d-flex align-items-baseline">
                        <i class="fa fa-map-marker fa-fw" role="img"
                            aria-label="Address" title="Address">
                        </i>
                        <span class="w-100 o_force_ltr d-block" itemprop="streetAddress"
                        >Adresse</span>
                    </div>
                </div>
            </address>
            """,
        )

    def test_render_with_data_page_break(self):
        template = self.env.ref("base.contact")
        template.arch = """<?xml version="1.0"?>
            <t t-name="base.contact">
                <table>
                    <tbody>
                        <tr qweb-table-page-break="">
                            <td>A1</td>
                            <td>B1</td>
                        </tr>
                        <tr qweb-table-page-break="avoid">
                            <td>A2</td>
                            <td>B2</td>
                        </tr>
                        <tr qweb-table-page-break="">
                            <td>A3</td>
                            <td>B3</td>
                        </tr>
                    </tbody>
                </table>
            </t>
        """
        self.assertHtml(
            self.env["ir.qweb"]._render("base.contact").decode("utf-8"),
            """
            <html>
                <body>
                    <table style="page-break-inside: avoid">
                        <tbody>
                            <tr>
                                <td>A1</td>
                                <td>B1</td>
                            </tr>
                        </tbody>
                    </table>
                    <table style="page-break-inside: avoid">
                        <tbody>
                            <tr>
                                <td>A2</td>
                                <td>B2</td>
                            </tr>
                            <tr>
                                <td>A3</td>
                                <td>B3</td>
                            </tr>
                        </tbody>
                    </table>
                </body>
            </html>
            """,
        )

    def test_split_tables(self):
        self.assertHtml(
            self.env["ir.qweb"]
            ._split_tables(
                b"""<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table>
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr qweb-table-page-break="ignore-unknown-value">
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr qweb-table-page-break="after">
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A4</td>
                                    <td>B4</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A5</td>
                                    <td>B5</td>
                                </tr>
                                <tr qweb-table-page-break="before">
                                    <td>A6</td>
                                    <td>B6</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A7</td>
                                    <td>B7</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A8</td>
                                    <td>B8</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>A9</td>
                                    <td>B9</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A10</td>
                                    <td>B10</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>"""
            )
            .decode("utf-8"),
            """<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="page-break-inside: avoid; page-break-after: always">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr>
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr>
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="page-break-inside: avoid; page-break-after: always">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A4</td>
                                    <td>B4</td>
                                </tr>
                                <tr>
                                    <td>A5</td>
                                    <td>B5</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A6</td>
                                    <td>B6</td>
                                </tr>
                                <tr>
                                    <td>A7</td>
                                    <td>B7</td>
                                </tr>
                                <tr>
                                    <td>A8</td>
                                    <td>B8</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A9</td>
                                    <td>B9</td>
                                </tr>
                                <tr>
                                    <td>A10</td>
                                    <td>B10</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>""",
        )

    def test_split_tables_with_existing_tbody_attributes(self):
        self.assertHtml(
            self.env["ir.qweb"]
            ._split_tables(
                b"""<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table>
                            <thead custom-attribute="test-thead">
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody custom-attribute="test-tbody">
                                <tr qweb-table-page-break="">
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>"""
            )
            .decode("utf-8"),
            """<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="page-break-inside: avoid">
                            <thead custom-attribute="test-thead">
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody custom-attribute="test-tbody">
                                <tr>
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="page-break-inside: avoid">
                            <thead custom-attribute="test-thead">
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody custom-attribute="test-tbody">
                                <tr>
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr>
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>""",
        )

    def test_split_tables_with_existing_style(self):
        self.assertHtml(
            self.env["ir.qweb"]
            ._split_tables(
                b"""<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="background-color: blue;">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr qweb-table-page-break="">
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>"""
            )
            .decode("utf-8"),
            """<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="background-color: blue; page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="background-color: blue; page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr>
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>""",
        )

    def test_split_tables_without_thead(self):
        self.assertHtml(
            self.env["ir.qweb"]
            ._split_tables(
                b"""<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table>
                            <tbody>
                                <tr qweb-table-page-break="">
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>"""
            )
            .decode("utf-8"),
            """<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="page-break-inside: avoid">
                            <tbody>
                                <tr>
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="page-break-inside: avoid">
                            <tbody>
                                <tr>
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr>
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>""",
        )

    def test_split_tables_with_existing_empty_style(self):
        self.assertHtml(
            self.env["ir.qweb"]
            ._split_tables(
                b"""<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr qweb-table-page-break="">
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>"""
            )
            .decode("utf-8"),
            """<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr>
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>""",
        )

    def test_split_tables_with_two_tables(self):
        self.assertHtml(
            self.env["ir.qweb"]
            ._split_tables(
                b"""<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="background-color: blue;">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr qweb-table-page-break="">
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="background-color: red;">
                            <thead>
                                <tr>
                                    <th>C</th>
                                    <th>D</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr qweb-table-page-break="">
                                    <td>C1</td>
                                    <td>D1</td>
                                </tr>
                                <tr qweb-table-page-break="avoid">
                                    <td>C2</td>
                                    <td>D2</td>
                                </tr>
                                <tr qweb-table-page-break="">
                                    <td>C3</td>
                                    <td>D3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>"""
            )
            .decode("utf-8"),
            """<html lang="fr-FR" web-base-url="http://localhost:8069">
                <head>
                    <meta charset="utf-8">
                    <meta name="viewport" content="initial-scale=1">
                    <title>Odoo Report</title>
                </head>
                <body>
                    <div>
                        <table style="background-color: blue; page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A1</td>
                                    <td>B1</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="background-color: blue; page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>A</th>
                                    <th>B</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>A2</td>
                                    <td>B2</td>
                                </tr>
                                <tr>
                                    <td>A3</td>
                                    <td>B3</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="background-color: red; page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>C</th>
                                    <th>D</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>C1</td>
                                    <td>D1</td>
                                </tr>
                            </tbody>
                        </table>
                        <table style="background-color: red; page-break-inside: avoid">
                            <thead>
                                <tr>
                                    <th>C</th>
                                    <th>D</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td>C2</td>
                                    <td>D2</td>
                                </tr>
                                <tr>
                                    <td>C3</td>
                                    <td>D3</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </body>
            </html>""",
        )

    def test_style_parser_empty_string(self):
        self.assertEqual(str(StyleParser("")), "")

    def test_style_parser_blank_string(self):
        self.assertEqual(str(StyleParser(" ")), "")

    def test_style_parser_wrong_formatted_string(self):
        self.assertEqual(
            str(
                StyleParser(
                    " test-not -a seto,g;background-color : "
                    " yellow  ;;; nice: value; other strange things"
                )
            ),
            "background-color: yellow; nice: value",
        )

    def test_style_parser_set_new_value(self):
        styles = StyleParser("background-color: yellow")
        styles.set("nice", "color")
        self.assertEqual(str(styles), "background-color: yellow; nice: color")

    def test_style_parser_set_existing_value(self):
        styles = StyleParser("background-color: yellow; nice: value")
        styles.set("nice", "color")
        self.assertEqual(str(styles), "background-color: yellow; nice: color")

    def test_style_parser_set_none_with_default_value_use_default(self):
        styles = StyleParser("background-color: yellow; nice: value")
        styles.set("nice", None, default="color")
        self.assertEqual(str(styles), "background-color: yellow; nice: color")

    def test_style_parser_set_none_without_default_value_remove_attribute(self):
        styles = StyleParser("background-color: yellow; nice: value")
        styles.set("nice", None)
        self.assertEqual(str(styles), "background-color: yellow")
