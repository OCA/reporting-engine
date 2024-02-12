from lxml import html

from odoo import api, models


class StyleParser:
    """Class to manipulate and Serialize/DeSerialize style attribute on
    html tag::

        style = StyleParser(element.get("style"))
        # set attribute page-break-inside
        style.set("page-break-inside", "avoid")
        # Serialize style to set style value on html element
        element.set("style", str(style))
    """

    _styles: dict = {}

    def __init__(self, style_content: str):
        self._parse(style_content)

    def _parse(self, style_content):
        self._styles = {}
        for style in style_content.split(";"):
            data_style = style.split(":")
            if len(data_style) != 2:
                # ignore if not expected string
                continue
            key, value = data_style
            self._styles[key.strip()] = value.strip()

    def __str__(self):
        return "; ".join([f"{k}: {v}" for k, v in self._styles.items()])

    def set(self, key, value, default=None):
        if value is None:
            value = default
        if value is None:
            self._styles.pop(key, None)
        else:
            self._styles[key] = value


class IrQWeb(models.AbstractModel):
    _inherit = "ir.qweb"

    @api.model
    def _render(self, id_or_xml_id, values=None, **options):
        result = super()._render(id_or_xml_id, values=values, **options)

        if b"qweb-table-page-break=" not in result:
            return result

        return self._split_tables(result)

    @api.model
    def _split_tables(self, html_content):
        html_document = html.document_fromstring(html_content.decode("utf-8"))

        for fragment in html_document:
            table = None
            for row in fragment.iterfind(".//tr[@qweb-table-page-break]"):
                # while generating pdf this method is called twice so we prevent
                # table to be split twice by removing qweb-table-page-break once
                # table has been splitted
                pos = row.attrib.pop("qweb-table-page-break")
                if pos not in ("before", "after", "avoid"):
                    continue
                table = next(row.iterancestors("table"))
                tbody = next(row.iterancestors("tbody"))
                newtable = html.Element("table", attrib=dict(table.attrib))
                newtbody = html.Element("tbody", attrib=dict(tbody.attrib))
                thead = table.find("thead")
                if thead is not None:
                    new_thead = html.fromstring(html.tostring(thead))
                    newtable.append(new_thead)
                newtable.append(newtbody)
                for sibling in row.getparent().iterchildren("tr"):
                    if sibling is row:
                        if pos == "after":
                            newtbody.append(sibling)
                        break
                    newtbody.append(sibling)
                table.addprevious(newtable)
                self._set_page_break_style(newtable, pos != "avoid")
                # this make sure we avoid break page inside the latest table parts
                # it's not a matter if this table is split in the next loop
                self._set_page_break_style(table, False)

        return html.tostring(
            html_document,
        )

    @api.model
    def _set_page_break_style(self, table, break_page_after):
        styles = StyleParser(table.get("style", ""))
        styles.set("page-break-inside", "avoid")
        if break_page_after:
            styles.set("page-break-after", "always")

        table.set("style", str(styles))
