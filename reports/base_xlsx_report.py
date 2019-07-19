# -*- coding: utf-8 -*-
# Part of hunghn. See LICENSE file for full copyright and licensing details.

from odoo import models, modules, _


class BaseXlsxReport(models.AbstractModel):
    _name = 'report.arch_construction.base_xlsx_report'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, objects):
        self.wb = workbook
        self.objects = objects
        self._define_formats()
        self.generate_sheets()
        self.set_layout(self.sheets)
        self.generate_main_content()

    def generate_sheets(self):
        self.sheets = [
            self.wb.add_worksheet('Sheet {}'.format(index + 1))
            for index in range(len(self.objects))
        ]

    def set_layout(self, sheets):
        for sheet in sheets:
            sheet.fit_to_pages(1, 0)
            sheet.set_header("")
            sheet.set_footer("Page &P of &N")
            sheet.set_margins(0.2, 0.3, 0.35, 0.15)
            sheet.center_horizontally()
            sheet.set_paper(9)
            self.set_cells_size(sheet)

    def generate_main_content(self):
        raise NotImplementedError()

    def set_cells_size(self, sheet):
        pass

    def _define_formats(self, default_font_size=12):
        normal_font = {
            'font_name': 'Times New Roman',
            'font_size': default_font_size,
            'text_wrap': True,
            'align': 'vcenter'
        }
        self.normal_font = self.wb.add_format(normal_font)

        normal_center = normal_font.copy()
        normal_center.update({
            'valign': 'vcenter',
            'align': 'center',
        })
        self.normal_center = self.wb.add_format(normal_center)

        normal_font_border_all = normal_font.copy()
        normal_font_border_all.update({
            'border': 1
        })
        self.normal_font_border_all = self.wb.add_format(
            normal_font_border_all)

        normal_font_border_center = normal_font.copy()
        normal_font_border_center.update({
            'border': 1,
            'valign': 'vcenter',
            'align': 'center',
        })
        self.normal_font_border_center = self.wb.add_format(
            normal_font_border_center)

        normal_right = normal_center.copy()
        normal_right.update({
            'align': 'right',
        })
        self.normal_right = self.wb.add_format(normal_right)

        normal_bold_font = normal_font.copy()
        normal_bold_font.update({
            'bold': True
        })
        self.normal_bold_font = self.wb.add_format(normal_bold_font)

        normal_bold_font_border_all = normal_bold_font.copy()
        normal_bold_font_border_all.update({
            'border': 1
        })
        self.normal_bold_font_border_all = self.wb.add_format(
            normal_bold_font_border_all
        )

        normal_bold_font_center = normal_bold_font.copy()
        normal_bold_font_center.update({
            'align': 'center',
        })
        self.normal_bold_font_center = self.wb.add_format(
            normal_bold_font_center)

        normal_number = normal_font.copy()
        normal_number.update({
            'num_format': '#,##0',
        })
        self.normal_number = self.wb.add_format(normal_number)

        normal_number_border_all = normal_number.copy()
        normal_number_border_all.update({
            'border': 1,
            'valign': 'vcenter',
            'align': 'center',
        })
        self.normal_number_border_all = self.wb.add_format(
            normal_number_border_all)

        header_font = normal_bold_font.copy()
        header_font.update({
            'font_size': 16,
            'valign': 'vcenter'
        })
        self.header_font = self.wb.add_format(header_font)

        header_center_font = normal_bold_font_center.copy()
        header_center_font.update({
            'font_size': 16,
            'valign': 'vcenter'
        })
        self.header_center_font = self.wb.add_format(header_center_font)

    def get_company_info(self):
        user = self.env.user
        company = user.company_id

        company_name = company.name
        company_tax = company.vat
        company_email = company.email
        company_website = company.website
        import base64
        import io
        company_logo = io.BytesIO(base64.b64decode(company.logo))
        company_address = '{street}, {street2}, {city}'.format(
            **{
                'street': company.street or '',
                'street2': company.street2 or '',
                'city': company.city or '',
                # 'country_name':
                #     company.country_id and company.country_id.name or '',
            }
        )
        company_phone = company.phone or ''
        return dict(company_name=company_name, company_logo=company_logo,
                    company_address=dict(
                        name_address=_('Address'),
                        company_address=company_address),
                    company_phone=dict(
                        name_phone=_('Phone'),
                        company_phone=company_phone),
                    company_tax=dict(
                        name_tax=_('TAX ID'),
                        company_tax=company_tax),
                    company_email=dict(
                        name_email=_('Email'),
                        company_email=company_email),
                    company_website=dict(
                        name_website=_('Website'),
                        company_website=company_website))
