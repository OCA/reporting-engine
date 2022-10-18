# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

from base64 import b64decode
from xml.dom import minidom

from lxml import etree

from odoo import api, models
from odoo.exceptions import ValidationError


class ReportXmlAbstract(models.AbstractModel):
    """
    Model `report.report_xml.abstract`.

    This class provide basic methods for rendering XML report and it's
    validation by XSD schema.
    """

    _name = "report.report_xml.abstract"
    _description = "Abstract XML Report"

    @api.model
    def generate_report(self, ir_report, docids, data=None):
        """
        Generate and validate XML report. Use incoming `ir_report` settings
        to setup encoding and XMl declaration for result `xml`.

        Methods:
         * `_get_rendering_context` `ir.actions.report` - get report variables.
         It will call `_get_report_values` of report's class if it's exist.
         * `render_template` of `ir.actions.report` - get report content
         * `validate_report` - check result content

        Args:
         * ir_report(`ir.actions.report`) - report definition instance in Odoo
         * docids(list) - IDs of instances for those report will be generated
         * data(dict, None) - variables for report rendering

        Returns:
         * str - result content of report
         * str - `"xml"`

        Extra Info:
         * Default encoding is `UTF-8`
        """
        # collect variable for rendering environment
        data = data or {}
        data.setdefault("report_type", "text")
        data = ir_report._get_rendering_context(ir_report, docids, data)

        # render template
        result_bin = ir_report._render_template(ir_report.report_name, data)

        # prettify result content
        # normalize indents
        parsed_result_bin = minidom.parseString(result_bin)
        result = parsed_result_bin.toprettyxml(indent="    ")

        # remove empty lines
        utf8 = "UTF-8"
        result = "\n".join(
            line for line in result.splitlines() if line and not line.isspace()
        ).encode(utf8)

        content = etree.tostring(
            etree.fromstring(result),
            encoding=ir_report.xml_encoding or utf8,
            xml_declaration=ir_report.xml_declaration,
            pretty_print=True,
        )

        # validate content
        xsd_schema_doc = ir_report.xsd_schema
        self.validate_report(xsd_schema_doc, content)
        return content, "xml"

    @api.model
    def validate_report(self, xsd_schema_doc, content):
        """
        Validate final report content against value of `xsd_schema` field
        ("XSD Validation Schema") of `ir.actions.report` via `etree` lib.

        Args:
         * xsd_schema_doc(byte-string) - report validation schema
         * content(str) - report content for validation

        Raises:
         * odoo.exceptions.ValidationError - Syntax of final report is wrong

        Returns:
         * bool - True
        """
        if xsd_schema_doc:
            # create validation parser
            decoded_xsd_schema_doc = b64decode(xsd_schema_doc)
            parsed_xsd_schema = etree.XML(decoded_xsd_schema_doc)
            xsd_schema = etree.XMLSchema(parsed_xsd_schema)
            parser = etree.XMLParser(schema=xsd_schema)

            try:
                # check content
                etree.fromstring(content, parser)
            except etree.XMLSyntaxError as error:
                raise ValidationError(error.msg) from error
        return True

    @api.model
    def _get_report_values(self, docids, data=None):
        """
        Allow to generate extra variables for report environment.

        Args:
         * docids(list) - IDs of instances for those report will be generated
         * data(dict, None) - variables for report rendering

        Returns:
         * dict - extra variables for report render
        """
        return data or {}
