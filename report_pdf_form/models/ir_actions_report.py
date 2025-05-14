# Copyright 2025 Camptocamp SA
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl)
import base64
import io

from pytz import timezone

from odoo import api, models
from odoo.exceptions import UserError
from odoo.tools import format_amount, format_date, format_datetime, pdf
from odoo.tools.float_utils import float_compare
from odoo.tools.pdf import (
    NameObject,
    NumberObject,
    PdfFileReader,
    PdfFileWriter,
    createStringObject,
)
from odoo.tools.safe_eval import datetime, dateutil, safe_eval, time


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    def _render_qweb_pdf_prepare_streams(self, report_ref, data, res_ids=None):
        pdf_form_report = self.env["report.pdf.form"].search(
            [("report_name", "=", report_ref)]
        )

        if not pdf_form_report:
            return super()._render_qweb_pdf_prepare_streams(
                report_ref, data, res_ids=res_ids
            )

        res = {}

        records = self.env[pdf_form_report.sudo().model_id.model].browse(res_ids)

        for rec in records:
            res[rec.id] = {"stream": None, "attachment": None}
            form_fields_values_mapping = {}
            writer = PdfFileWriter()

            self_with_rec_context = self.with_context(
                # TODO Add check/option if record has partner_id field?
                # use_babel=True, lang=rec.partner_id.lang or self.env.user.lang
                use_babel=True,
                lang=self.env.user.lang,
            )
            prefix = f"template_{pdf_form_report.id}__"
            self_with_rec_context._update_mapping_and_add_pages_to_writer_pdf(
                writer, pdf_form_report, form_fields_values_mapping, prefix, rec
            )

            pdf.fill_form_fields_pdf(writer, form_fields=form_fields_values_mapping)
            with io.BytesIO() as _buffer:
                writer.write(_buffer)
                stream = io.BytesIO(_buffer.getvalue())
            res[rec.id].update({"stream": stream})
        return res

    @api.model
    def _update_mapping_and_add_pages_to_writer_pdf(
        self, writer, template, form_fields_values_mapping, prefix, record
    ):
        for form_field in template.field_mapping_ids:
            if form_field.odoo_field_evaluation == "dotted_path":
                field_value = self._get_pdf_value_from_path(form_field, record)
            elif form_field.odoo_field_evaluation == "text":
                field_value = form_field.odoo_field_value
            elif form_field.odoo_field_evaluation == "code":
                field_value = self._get_pdf_value_from_code(form_field, record)
            elif form_field.odoo_field_evaluation == "repeat_field":
                continue
            else:
                raise UserError(self.env._("Invalid evaluation for Odoo field"))
            form_fields_values_mapping[prefix + form_field.pdf_field_name] = field_value

        for form_field in template.field_mapping_ids.filtered(
            lambda fld: fld.odoo_field_evaluation == "repeat_field"
        ):
            form_fields_values_mapping[prefix + form_field.pdf_field_name] = (
                form_fields_values_mapping[prefix + form_field.odoo_field_value]
            )

        decoded_template = base64.b64decode(template.sudo().pdf_attachment_id.datas)
        self._add_pages_to_writer_pdf(writer, decoded_template, prefix)

    @api.model
    def _get_pdf_value_from_code(self, form_field, record):
        return safe_eval(
            form_field.odoo_field_value,
            self._pdf_form_eval_context(record, form_field.report_form_id),
        )

    def _pdf_form_eval_context(self, record, template):
        base_ctx = {
            "record": record.sudo(),
            "env": record.env,
            "time": time,
            "datetime": datetime,
            "dateutil": dateutil,
            "timezone": timezone,
            "float_compare": float_compare,
        }
        res = base_ctx.copy()
        for var in template.field_variable_ids:
            res[var.name] = safe_eval(var.code, base_ctx)
        return res

    @api.model
    def _get_pdf_value_from_path(self, form_field, record):
        tz = record.env.user.tz or "UTC"
        base_record = record
        path = form_field.odoo_field_value
        # If path = 'order_id.order_line.product_id.name'
        path = path.split(".")  # ['order_id', 'order_line', 'product_id', 'name']
        # Sudo to be able to follow the path set by the admin
        records = base_record.sudo().mapped(
            ".".join(path[:-1])
        )  # product.product(id1, id2, ...)
        field_name = path[-1]  # 'name'

        def _get_formatted_value(self):
            # self must be named so to be considered in the translation logic
            field_ = records._fields[field_name]
            field_type_ = field_.type
            for record_ in records:
                value_ = record_[field_name]
                if field_type_ == "boolean":
                    formatted_value_ = self.env._("Yes") if value_ else self.env._("No")
                elif field_type_ == "monetary":
                    currency_id_ = record_[field_.get_currency_field(record_)]
                    formatted_value_ = format_amount(
                        self.env, value_, currency_id_ or record_.currency_id
                    )
                elif not value_:
                    formatted_value_ = ""
                elif field_type_ == "date":
                    formatted_value_ = format_date(self.env, value_)
                elif field_type_ == "datetime":
                    formatted_value_ = format_datetime(
                        self.env, value_, tz=tz, dt_format=False
                    )
                elif field_type_ == "selection" and value_:
                    formatted_value_ = dict(field_._description_selection(self.env))[
                        value_
                    ]
                elif field_type_ in {"one2many", "many2one", "many2many"}:
                    formatted_value_ = ", ".join([v.display_name for v in value_])
                else:
                    formatted_value_ = str(value_)

                yield formatted_value_

        return ", ".join(_get_formatted_value(self))

    @api.model
    def _add_pages_to_writer_pdf(self, writer, document, prefix=None):
        reader = PdfFileReader(io.BytesIO(document), strict=False)

        field_names = set()
        if prefix:
            field_names = reader.getFormTextFields()

        for page_id in range(reader.getNumPages()):
            page = reader.getPage(page_id)
            if prefix and page.get("/Annots"):
                # Modifying the annots that hold every information about the form fields
                for j in range(len(page["/Annots"])):
                    reader_annot = page["/Annots"][j].getObject()
                    if reader_annot.get("/T") in field_names:
                        # Prefix all form fields in the document with the document
                        #  identifier.
                        # This is necessary to know which value needs to be taken when
                        #  filling the forms.
                        form_key = reader_annot.get("/T")
                        new_key = prefix + form_key

                        # Modifying the form flags to force some characteristics
                        # 1. make all text fields read-only
                        # 2. make all text fields support multiline
                        form_flags = reader_annot.get("/Ff", 0)
                        readonly_flag = 1  # 1st bit sets readonly
                        multiline_flag = 1 << 12  # 13th bit sets multiline text
                        new_flags = form_flags | readonly_flag | multiline_flag

                        reader_annot.update(
                            {
                                NameObject("/T"): createStringObject(new_key),
                                NameObject("/Ff"): NumberObject(new_flags),
                            }
                        )
            writer.addPage(page)
