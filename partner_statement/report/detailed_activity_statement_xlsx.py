# Author: Miquel Raïch
# Copyright 2022 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, models

from odoo.addons.report_xlsx_helper.report.report_xlsx_format import FORMATS


def copy_format(book, fmt):
    properties = [f[4:] for f in dir(fmt) if f[0:4] == "set_"]
    dft_fmt = book.add_format()
    return book.add_format(
        {
            k: v
            for k, v in fmt.__dict__.items()
            if k in properties and dft_fmt.__dict__[k] != v
        }
    )


class DetailedActivityStatementXslx(models.AbstractModel):
    _name = "report.p_s.report_detailed_activity_statement_xlsx"
    _description = "Detailed Activity Statement XLSL Report"
    _inherit = "report.p_s.report_activity_statement_xlsx"

    def _get_report_name(self, report, data=False):
        company_id = data.get("company_id", False)
        report_name = _("Detailed Activity Statement")
        if company_id:
            company = self.env["res.company"].browse(company_id)
            suffix = " - {} - {}".format(company.name, company.currency_id.name)
            report_name = report_name + suffix
        return report_name

    def _write_currency_lines(self, row_pos, sheet, partner, currency, data):
        partner_data = data.get("data", {}).get(partner.id, {})
        currency_data = partner_data.get("currencies", {}).get(currency.id)
        account_type = data.get("account_type", False)
        row_pos += 2
        statement_header = _(
            "Detailed %(payable)sStatement between %(start)s and %(end)s in %(currency)s"
        ) % {
            "payable": account_type == "liability_payable" and _("Supplier ") or "",
            "start": partner_data.get("start"),
            "end": partner_data.get("end"),
            "currency": currency.display_name,
        }
        sheet.merge_range(
            row_pos,
            0,
            row_pos,
            6,
            statement_header,
            FORMATS["format_left_bold"],
        )
        row_pos += 1
        sheet.write(
            row_pos, 0, _("Reference Number"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 1, _("Date"), FORMATS["format_theader_yellow_center"])
        sheet.merge_range(
            row_pos,
            2,
            row_pos,
            3,
            _("Description"),
            FORMATS["format_theader_yellow_center"],
        )
        sheet.write(
            row_pos, 4, _("Original Amount"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(
            row_pos, 5, _("Applied Amount"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(
            row_pos, 6, _("Open Amount"), FORMATS["format_theader_yellow_center"]
        )
        row_pos += 1
        sheet.write(
            row_pos, 1, partner_data.get("prior_day"), FORMATS["format_tcell_date_left"]
        )
        sheet.merge_range(
            row_pos,
            2,
            row_pos,
            5,
            _("Initial Balance"),
            FORMATS["format_tcell_left"],
        )
        sheet.write(
            row_pos,
            6,
            currency_data.get("balance_forward"),
            FORMATS["current_money_format"],
        )
        for line in currency_data.get("lines"):
            if line.get("blocked") and not line.get("reconciled_line"):
                format_tcell_left = FORMATS["format_tcell_left_blocked"]
                format_tcell_date_left = FORMATS["format_tcell_date_left_blocked"]
                format_distributed = FORMATS["format_distributed_blocked"]
                current_money_format = FORMATS["current_money_format_blocked"]
            elif (
                line.get("reconciled_line")
                and not line.get("blocked")
                and not line.get("outside-date-rank")
            ):
                format_tcell_left = FORMATS["format_tcell_left_reconciled"]
                format_tcell_date_left = FORMATS["format_tcell_date_left_reconciled"]
                format_distributed = FORMATS["format_distributed_reconciled"]
                current_money_format = FORMATS["current_money_format_reconciled"]
            elif (
                line.get("blocked")
                and line.get("reconciled_line")
                and not line.get("outside-date-rank")
            ):
                format_tcell_left = FORMATS["format_tcell_left_blocked_reconciled"]
                format_tcell_date_left = FORMATS[
                    "format_tcell_date_left_blocked_reconciled"
                ]
                format_distributed = FORMATS["format_distributed_blocked_reconciled"]
                current_money_format = FORMATS[
                    "current_money_format_blocked_reconciled"
                ]
            elif (
                line.get("reconciled_line")
                and not line.get("blocked")
                and line.get("outside-date-rank")
            ):
                format_tcell_left = FORMATS[
                    "format_tcell_left_reconciled_outside-date-rank"
                ]
                format_tcell_date_left = FORMATS[
                    "format_tcell_date_left_reconciled_outside-date-rank"
                ]
                format_distributed = FORMATS[
                    "format_distributed_reconciled_outside-date-rank"
                ]
                current_money_format = FORMATS[
                    "current_money_format_reconciled_outside-date-rank"
                ]
            elif (
                line.get("blocked")
                and line.get("reconciled_line")
                and line.get("outside-date-rank")
            ):
                format_tcell_left = FORMATS[
                    "format_tcell_left_blocked_reconciled_outside-date-rank"
                ]
                format_tcell_date_left = FORMATS[
                    "format_tcell_date_left_blocked_reconciled_outside-date-rank"
                ]
                format_distributed = FORMATS[
                    "format_distributed_blocked_reconciled_outside-date-rank"
                ]
                current_money_format = FORMATS[
                    "current_money_format_blocked_reconciled_outside-date-rank"
                ]
            else:
                format_tcell_left = FORMATS["format_tcell_left"]
                format_tcell_date_left = FORMATS["format_tcell_date_left"]
                format_distributed = FORMATS["format_distributed"]
                current_money_format = FORMATS["current_money_format"]
            row_pos += 1
            name_to_show = (
                line.get("name", "") == "/" or not line.get("name", "")
            ) and line.get("ref", "")
            if line.get("name", "") and line.get("name", "") != "/":
                if not line.get("ref", ""):
                    name_to_show = line.get("name", "")
                else:
                    if (line.get("name", "") in line.get("ref", "")) or (
                        line.get("name", "") == line.get("ref", "")
                    ):
                        name_to_show = line.get("name", "")
                    elif line.get("ref", "") not in line.get("name", ""):
                        name_to_show = line.get("ref", "")
            sheet.write(row_pos, 0, line.get("move_id", ""), format_tcell_left)
            sheet.write(row_pos, 1, line.get("date", ""), format_tcell_date_left)
            sheet.merge_range(row_pos, 2, row_pos, 3, name_to_show, format_distributed)
            sheet.write(
                row_pos,
                4,
                line.get("amount", "") if not line.get("reconciled_line") else "",
                current_money_format,
            )
            sheet.write(
                row_pos, 5, line.get("applied_amount", ""), current_money_format
            )
            sheet.write(
                row_pos,
                6,
                line.get("open_amount", "") if not line.get("reconciled_line") else "",
                current_money_format,
            )
        row_pos += 1
        sheet.write(
            row_pos, 1, partner_data.get("end"), FORMATS["format_tcell_date_left"]
        )
        sheet.merge_range(
            row_pos,
            2,
            row_pos,
            5,
            _("Ending Balance"),
            FORMATS["format_tcell_left"],
        )
        sheet.write(
            row_pos,
            6,
            currency_data.get("amount_due"),
            FORMATS["current_money_format"],
        )
        return row_pos

    def _write_currency_prior_lines(self, row_pos, sheet, partner, currency, data):
        partner_data = data.get("data", {}).get(partner.id, {})
        currency_data = partner_data.get("currencies", {}).get(currency.id)
        account_type = data.get("account_type", False)
        row_pos += 2
        statement_header = _(
            "%(payable)sStatement up to %(prior_day)s in %(currency)s"
        ) % {
            "payable": account_type == "payable" and _("Supplier ") or "",
            "prior_day": partner_data.get("prior_day"),
            "currency": currency.display_name,
        }
        sheet.merge_range(
            row_pos,
            0,
            row_pos,
            6,
            statement_header,
            FORMATS["format_left_bold"],
        )
        row_pos += 1
        sheet.write(
            row_pos, 0, _("Reference Number"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 1, _("Date"), FORMATS["format_theader_yellow_center"])
        sheet.write(row_pos, 2, _("Due Date"), FORMATS["format_theader_yellow_center"])
        sheet.write(
            row_pos,
            3,
            _("Description"),
            FORMATS["format_theader_yellow_center"],
        )
        sheet.write(row_pos, 4, _("Original"), FORMATS["format_theader_yellow_center"])
        sheet.write(
            row_pos, 5, _("Open Amount"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 6, _("Balance"), FORMATS["format_theader_yellow_center"])
        format_tcell_left = FORMATS["format_tcell_left"]
        format_tcell_date_left = FORMATS["format_tcell_date_left"]
        format_distributed = FORMATS["format_distributed"]
        current_money_format = FORMATS["current_money_format"]
        for line in currency_data.get("prior_lines"):
            if line.get("blocked") and not line.get("reconciled_line"):
                format_tcell_left = FORMATS["format_tcell_left_blocked"]
                format_tcell_date_left = FORMATS["format_tcell_date_left_blocked"]
                format_distributed = FORMATS["format_distributed_blocked"]
                current_money_format = FORMATS["current_money_format_blocked"]
            elif line.get("reconciled_line") and not line.get("blocked"):
                format_tcell_left = FORMATS["format_tcell_left_reconciled"]
                format_tcell_date_left = FORMATS["format_tcell_date_left_reconciled"]
                format_distributed = FORMATS["format_distributed_reconciled"]
                current_money_format = FORMATS["current_money_format_reconciled"]
            elif line.get("blocked") and line.get("reconciled_line"):
                format_tcell_left = FORMATS["format_tcell_left_blocked_reconciled"]
                format_tcell_date_left = FORMATS[
                    "format_tcell_date_left_blocked_reconciled"
                ]
                format_distributed = FORMATS["format_distributed_blocked_reconciled"]
                current_money_format = FORMATS[
                    "current_money_format_blocked_reconciled"
                ]
            row_pos += 1
            name_to_show = (
                line.get("name", "") == "/" or not line.get("name", "")
            ) and line.get("ref", "")
            if line.get("name", "") and line.get("name", "") != "/":
                if not line.get("ref", ""):
                    name_to_show = line.get("name", "")
                else:
                    if (line.get("ref", "") in line.get("name", "")) or (
                        line.get("name", "") == line.get("ref", "")
                    ):
                        name_to_show = line.get("name", "")
                    else:
                        name_to_show = line.get("ref", "")
            sheet.write(row_pos, 0, line.get("move_id", ""), format_tcell_left)
            sheet.write(row_pos, 1, line.get("date", ""), format_tcell_date_left)
            sheet.write(
                row_pos,
                2,
                line.get("date_maturity", ""),
                format_tcell_date_left,
            )
            sheet.write(row_pos, 3, name_to_show, format_distributed)
            sheet.write(row_pos, 4, line.get("amount", ""), current_money_format)
            sheet.write(row_pos, 5, line.get("open_amount", ""), current_money_format)
            sheet.write(row_pos, 6, line.get("balance", ""), current_money_format)
        row_pos += 1
        sheet.write(
            row_pos, 1, partner_data.get("prior_day"), FORMATS["format_tcell_date_left"]
        )
        sheet.merge_range(
            row_pos,
            2,
            row_pos,
            5,
            _("Ending Balance"),
            FORMATS["format_tcell_left"],
        )
        sheet.write(
            row_pos,
            6,
            currency_data.get("balance_forward"),
            FORMATS["current_money_format"],
        )
        return row_pos

    def _write_currency_ending_lines(self, row_pos, sheet, partner, currency, data):
        partner_data = data.get("data", {}).get(partner.id, {})
        currency_data = partner_data.get("currencies", {}).get(currency.id)
        account_type = data.get("account_type", False)
        row_pos += 2
        statement_header = _("%(payable)sStatement up to %(end)s in %(currency)s") % {
            "payable": account_type == "payable" and _("Supplier ") or "",
            "end": partner_data.get("end"),
            "currency": currency.display_name,
        }
        sheet.merge_range(
            row_pos,
            0,
            row_pos,
            6,
            statement_header,
            FORMATS["format_left_bold"],
        )
        row_pos += 1
        sheet.write(
            row_pos, 0, _("Reference Number"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 1, _("Date"), FORMATS["format_theader_yellow_center"])
        sheet.write(row_pos, 2, _("Due Date"), FORMATS["format_theader_yellow_center"])
        sheet.write(
            row_pos,
            3,
            _("Description"),
            FORMATS["format_theader_yellow_center"],
        )
        sheet.write(row_pos, 4, _("Original"), FORMATS["format_theader_yellow_center"])
        sheet.write(
            row_pos, 5, _("Open Amount"), FORMATS["format_theader_yellow_center"]
        )
        sheet.write(row_pos, 6, _("Balance"), FORMATS["format_theader_yellow_center"])
        format_tcell_left = FORMATS["format_tcell_left"]
        format_tcell_date_left = FORMATS["format_tcell_date_left"]
        format_distributed = FORMATS["format_distributed"]
        current_money_format = FORMATS["current_money_format"]
        for line in currency_data.get("ending_lines"):
            if line.get("blocked") and not line.get("reconciled_line"):
                format_tcell_left = FORMATS["format_tcell_left_blocked"]
                format_tcell_date_left = FORMATS["format_tcell_date_left_blocked"]
                format_distributed = FORMATS["format_distributed_blocked"]
                current_money_format = FORMATS["current_money_format_blocked"]
            elif line.get("reconciled_line") and not line.get("blocked"):
                format_tcell_left = FORMATS["format_tcell_left_reconciled"]
                format_tcell_date_left = FORMATS["format_tcell_date_left_reconciled"]
                format_distributed = FORMATS["format_distributed_reconciled"]
                current_money_format = FORMATS["current_money_format_reconciled"]
            elif line.get("blocked") and line.get("reconciled_line"):
                format_tcell_left = FORMATS["format_tcell_left_blocked_reconciled"]
                format_tcell_date_left = FORMATS[
                    "format_tcell_date_left_blocked_reconciled"
                ]
                format_distributed = FORMATS["format_distributed_blocked_reconciled"]
                current_money_format = FORMATS[
                    "current_money_format_blocked_reconciled"
                ]
            row_pos += 1
            name_to_show = (
                line.get("name", "") == "/" or not line.get("name", "")
            ) and line.get("ref", "")
            if line.get("name", "") and line.get("name", "") != "/":
                if not line.get("ref", ""):
                    name_to_show = line.get("name", "")
                else:
                    if (line.get("ref", "") in line.get("name", "")) or (
                        line.get("name", "") == line.get("ref", "")
                    ):
                        name_to_show = line.get("name", "")
                    else:
                        name_to_show = line.get("ref", "")
            sheet.write(row_pos, 0, line.get("move_id", ""), format_tcell_left)
            sheet.write(row_pos, 1, line.get("date", ""), format_tcell_date_left)
            sheet.write(
                row_pos,
                2,
                line.get("date_maturity", ""),
                format_tcell_date_left,
            )
            sheet.write(row_pos, 3, name_to_show, format_distributed)
            sheet.write(row_pos, 4, line.get("amount", ""), current_money_format)
            sheet.write(row_pos, 5, line.get("open_amount", ""), current_money_format)
            sheet.write(row_pos, 6, line.get("balance", ""), current_money_format)
        row_pos += 1
        sheet.write(
            row_pos, 1, partner_data.get("end"), FORMATS["format_tcell_date_left"]
        )
        sheet.merge_range(
            row_pos,
            2,
            row_pos,
            5,
            _("Ending Balance"),
            FORMATS["format_tcell_left"],
        )
        sheet.write(
            row_pos,
            6,
            currency_data.get("amount_due"),
            FORMATS["current_money_format"],
        )
        return row_pos

    def _size_columns(self, sheet, data):
        for i in range(7):
            sheet.set_column(0, i, 20)

    def generate_xlsx_report(self, workbook, data, objects):
        lang = objects.lang or self.env.user.partner_id.lang
        self = self.with_context(lang=lang)
        report_model = self.env["report.partner_statement.detailed_activity_statement"]
        self._define_formats(workbook)
        FORMATS["format_distributed"] = workbook.add_format({"align": "vdistributed"})
        company_id = data.get("company_id", False)
        if company_id:
            company = self.env["res.company"].browse(company_id)
        else:
            company = self.env.user.company_id
        data.update(report_model._get_report_values(data.get("partner_ids"), data))
        partners = self.env["res.partner"].browse(data.get("partner_ids"))
        sheet = workbook.add_worksheet(_("Detailed Activity Statement"))
        sheet.set_landscape()
        row_pos = 0
        sheet.merge_range(
            row_pos,
            0,
            row_pos,
            6,
            _("Statement of Account from %s") % (company.display_name,),
            FORMATS["format_ws_title"],
        )
        row_pos += 1
        sheet.write(row_pos, 1, _("Date:"), FORMATS["format_theader_yellow_right"])
        sheet.write(
            row_pos,
            2,
            data.get("data", {}).get(partners.ids[0], {}).get("today"),
            FORMATS["format_date_left"],
        )
        self._size_columns(sheet, data)
        for partner in partners:
            invoice_address = data.get(
                "get_inv_addr", lambda x: self.env["res.partner"]
            )(partner)
            row_pos += 3
            sheet.write(
                row_pos, 1, _("Statement to:"), FORMATS["format_theader_yellow_right"]
            )
            sheet.merge_range(
                row_pos,
                2,
                row_pos,
                3,
                invoice_address.display_name,
                FORMATS["format_left"],
            )
            if invoice_address.vat:
                sheet.write(
                    row_pos,
                    4,
                    _("VAT:"),
                    FORMATS["format_theader_yellow_right"],
                )
                sheet.write(
                    row_pos,
                    5,
                    invoice_address.vat,
                    FORMATS["format_left"],
                )
            row_pos += 1
            sheet.write(
                row_pos, 1, _("Statement from:"), FORMATS["format_theader_yellow_right"]
            )
            sheet.merge_range(
                row_pos,
                2,
                row_pos,
                3,
                company.partner_id.display_name,
                FORMATS["format_left"],
            )
            if company.vat:
                sheet.write(
                    row_pos,
                    4,
                    _("VAT:"),
                    FORMATS["format_theader_yellow_right"],
                )
                sheet.write(
                    row_pos,
                    5,
                    company.vat,
                    FORMATS["format_left"],
                )
            partner_data = data.get("data", {}).get(partner.id)
            currencies = partner_data.get("currencies", {}).keys()
            if currencies:
                row_pos += 1
            for currency_id in currencies:
                currency = self.env["res.currency"].browse(currency_id)
                if currency.position == "after":
                    money_string = "#,##0.%s " % (
                        "0" * currency.decimal_places
                    ) + "[${}]".format(currency.symbol)
                elif currency.position == "before":
                    money_string = "[${}]".format(currency.symbol) + " #,##0.%s" % (
                        "0" * currency.decimal_places
                    )
                FORMATS["current_money_format"] = workbook.add_format(
                    {"align": "right", "num_format": money_string}
                )
                bg_grey = "#ADB5BD"
                fc_red = "#DC3545"
                FORMATS["format_tcell_left_blocked"] = copy_format(
                    workbook, FORMATS["format_tcell_left"]
                )
                FORMATS["format_tcell_left_blocked"].set_bg_color(bg_grey)
                FORMATS["format_tcell_date_left_blocked"] = copy_format(
                    workbook, FORMATS["format_tcell_date_left"]
                )
                FORMATS["format_tcell_date_left_blocked"].set_bg_color(bg_grey)
                FORMATS["format_distributed_blocked"] = copy_format(
                    workbook, FORMATS["format_distributed"]
                )
                FORMATS["format_distributed_blocked"].set_bg_color(bg_grey)
                FORMATS["current_money_format_blocked"] = copy_format(
                    workbook, FORMATS["current_money_format"]
                )
                FORMATS["current_money_format_blocked"].set_bg_color(bg_grey)
                FORMATS["format_tcell_left_reconciled"] = copy_format(
                    workbook, FORMATS["format_tcell_left"]
                )
                FORMATS["format_tcell_left_reconciled"].set_italic(True)
                FORMATS["format_tcell_left_reconciled"].set_font_size(10)
                FORMATS["format_tcell_left_reconciled"].set_indent(1)
                FORMATS["format_tcell_date_left_reconciled"] = copy_format(
                    workbook, FORMATS["format_tcell_date_left"]
                )
                FORMATS["format_tcell_date_left_reconciled"].set_italic(True)
                FORMATS["format_tcell_date_left_reconciled"].set_font_size(10)
                FORMATS["format_distributed_reconciled"] = copy_format(
                    workbook, FORMATS["format_distributed"]
                )
                FORMATS["format_distributed_reconciled"].set_italic(True)
                FORMATS["format_distributed_reconciled"].set_font_size(10)
                FORMATS["current_money_format_reconciled"] = copy_format(
                    workbook, FORMATS["current_money_format"]
                )
                FORMATS["current_money_format_reconciled"].set_italic(True)
                FORMATS["current_money_format_reconciled"].set_font_size(10)
                FORMATS["format_tcell_left_blocked_reconciled"] = copy_format(
                    workbook, FORMATS["format_tcell_left_reconciled"]
                )
                FORMATS["format_tcell_left_blocked_reconciled"].set_bg_color(bg_grey)
                FORMATS["format_tcell_date_left_blocked_reconciled"] = copy_format(
                    workbook, FORMATS["format_tcell_date_left_reconciled"]
                )
                FORMATS["format_tcell_date_left_blocked_reconciled"].set_bg_color(
                    bg_grey
                )
                FORMATS["format_distributed_blocked_reconciled"] = copy_format(
                    workbook, FORMATS["format_distributed_reconciled"]
                )
                FORMATS["format_distributed_blocked_reconciled"].set_bg_color(bg_grey)
                FORMATS["current_money_format_blocked_reconciled"] = copy_format(
                    workbook, FORMATS["current_money_format_reconciled"]
                )
                FORMATS["current_money_format_blocked_reconciled"].set_bg_color(bg_grey)
                FORMATS["format_tcell_left_reconciled_outside-date-rank"] = copy_format(
                    workbook, FORMATS["format_tcell_left_reconciled"]
                )
                FORMATS[
                    "format_tcell_left_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "format_tcell_date_left_reconciled_outside-date-rank"
                ] = copy_format(workbook, FORMATS["format_tcell_date_left_reconciled"])
                FORMATS[
                    "format_tcell_date_left_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "format_distributed_reconciled_outside-date-rank"
                ] = copy_format(workbook, FORMATS["format_distributed_reconciled"])
                FORMATS[
                    "format_distributed_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "current_money_format_reconciled_outside-date-rank"
                ] = copy_format(workbook, FORMATS["current_money_format_reconciled"])
                FORMATS[
                    "current_money_format_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "format_tcell_left_blocked_reconciled_outside-date-rank"
                ] = copy_format(
                    workbook, FORMATS["format_tcell_left_blocked_reconciled"]
                )
                FORMATS[
                    "format_tcell_left_blocked_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "format_tcell_date_left_blocked_reconciled_outside-date-rank"
                ] = copy_format(
                    workbook, FORMATS["format_tcell_date_left_blocked_reconciled"]
                )
                FORMATS[
                    "format_tcell_date_left_blocked_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "format_distributed_blocked_reconciled_outside-date-rank"
                ] = copy_format(
                    workbook, FORMATS["format_distributed_blocked_reconciled"]
                )
                FORMATS[
                    "format_distributed_blocked_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                FORMATS[
                    "current_money_format_blocked_reconciled_outside-date-rank"
                ] = copy_format(
                    workbook, FORMATS["current_money_format_blocked_reconciled"]
                )
                FORMATS[
                    "current_money_format_blocked_reconciled_outside-date-rank"
                ].set_font_color(fc_red)
                row_pos = self._write_currency_prior_lines(
                    row_pos, sheet, partner, currency, data
                )
                row_pos = self._write_currency_lines(
                    row_pos, sheet, partner, currency, data
                )
                row_pos = self._write_currency_ending_lines(
                    row_pos, sheet, partner, currency, data
                )
                row_pos = self._write_currency_buckets(
                    row_pos, sheet, partner, currency, data
                )
