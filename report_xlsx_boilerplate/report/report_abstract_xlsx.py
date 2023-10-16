# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

from odoo import _, api, models
from odoo.exceptions import ValidationError
from odoo.modules.module import get_module_resource

from .utils.xlsx_utils import HORIZ_ALIG_ACPTD_VALS, VERT_ALIG_ACPTD_VALS

_logger = logging.getLogger(__name__)

try:
    import openpyxl
except ImportError:
    _logger.debug("Can't import openpyxl.")


class ReportXlsxAbstract(models.AbstractModel):
    _inherit = "report.report_xlsx.abstract"

    # Path relative to the module location
    _boilerplate_template_file_path = None

    @api.model
    def _get_module_name_from_model_name(self):
        """
        The _name of the model will always have the following structure:
        `report.{module_name}.{report_name}`
        """
        return self._name.split(".")[1]

    @api.model
    def get_workbook(self, file_data):
        if self._boilerplate_template_file_path is not None:
            return self._get_boilerplate_template(file_data)
        return super().get_workbook(file_data)

    def _get_boilerplate_template(self, file_data):
        """
        :return: copy of the Boilerplate Template of the report if everything is
        correctly set up, blank workbook otherwise
        :rtype: xlsxwriter.Workbook object
        """
        module = self._get_module_name_from_model_name()
        module_path, file_name = self._boilerplate_template_file_path.rsplit("/", 1)
        file_path = get_module_resource(module, module_path, file_name)
        if not file_path:
            raise ValidationError(
                _(
                    "Boilerplate Template file path not properly defined: %s."
                    % self._boilerplate_template_file_path
                )
            )
        try:
            boilerplate_template = openpyxl.load_workbook(file_path)
            return self._copy_xlsx(file_data, boilerplate_template)
        except Exception as e:
            _logger.exception(e)
            return self._get_new_workbook(file_data)

    # flake8: noqa: C901
    @api.model
    def _copy_cell_format(self, xlsx, cell):
        """
        :return: a format object that needs to be applied coming from the
        openyxl.cell.cell.Cell object
        :rtype: xlsxwriter.format.Format
        """
        cell_format = xlsx.add_format()
        values_dict = dict()
        bs_field = "border_style"
        if hasattr(cell.fill.bgColor, "rgb") and cell.fill.bgColor.value != "00000000":
            bg_color = "#" + cell.fill.bgColor.rgb[2:]
            values_dict.setdefault("bg_color", bg_color)
        if cell.font:
            if hasattr(cell.font.color, "rgb"):
                font_color = "#" + cell.font.color.rgb[2:]
                values_dict.setdefault("font_color", font_color)
            if cell.font.b:
                values_dict.setdefault("bold", cell.font.b)
            if cell.font.i:
                values_dict.setdefault("italic", cell.font.i)
            if cell.font.u:
                values_dict.setdefault("underline", cell.font.u)
        if cell.alignment:
            if cell.alignment.wrapText:
                values_dict.setdefault("text_wrap", cell.alignment.wrapText)
            values_dict.setdefault("align", list())
            if cell.alignment.horizontal in HORIZ_ALIG_ACPTD_VALS.keys():
                values_dict["align"].append(
                    HORIZ_ALIG_ACPTD_VALS.get(cell.alignment.horizontal)
                )
            if cell.alignment.vertical in VERT_ALIG_ACPTD_VALS.keys():
                values_dict["align"].append(
                    VERT_ALIG_ACPTD_VALS.get(cell.alignment.vertical)
                )
        for side in ["left", "right", "top", "bottom"]:
            if hasattr(cell.border, side) and hasattr(
                getattr(cell.border, side), bs_field
            ):
                values_dict.setdefault(side, 1)
        for key, value in values_dict.items():
            func_name = "set_%s" % key
            if hasattr(cell_format, func_name):
                if isinstance(value, list):
                    if not value:
                        continue
                    values_to_assign = value
                else:
                    values_to_assign = [value]
                for val in values_to_assign:
                    getattr(cell_format, func_name)(val)
        return cell_format

    def _copy_xlsx(self, file_data, template_xlsx):
        """
        :return: a copy of the openpyxl.Workbook object on a xlsxwriter.Workbook object. Converts all the content from one type of object to the other
        :rtype: xlsxwriter.Workbook object
        """
        new_xlsx = self._get_new_workbook(file_data)
        template_sheets = template_xlsx.get_sheet_names()
        for sheet_name in template_sheets:
            new_xlsx.add_worksheet(sheet_name)
        for sheet in template_sheets:
            openpyxl_active_sheet = template_xlsx.get_sheet_by_name(sheet)
            xlsxwriter_active_sheet = new_xlsx.get_worksheet_by_name(sheet)
            for count, row in enumerate(openpyxl_active_sheet.rows):
                for cell in row:
                    if isinstance(cell, openpyxl.cell.cell.MergedCell):
                        continue
                    else:
                        # 1. Set Column Width
                        column_index = cell.column - 1
                        cell_width = openpyxl_active_sheet.column_dimensions[
                            cell.column_letter
                        ].width
                        xlsxwriter_active_sheet.set_column(
                            column_index, column_index, cell_width
                        )
                        # 2. Set Cell Format for each cell
                        cell_format = self._copy_cell_format(new_xlsx, cell)
                        xlsxwriter_active_sheet.write(
                            cell.coordinate, cell.value, cell_format
                        )
                # 3. Set Row Height for each row
                row_index = cell.row - 1
                cell_height = openpyxl_active_sheet.row_dimensions[cell.row].height
                xlsxwriter_active_sheet.set_row(row_index, cell_height)
            # 4. Merge merged cells at the end
            for merge_range in openpyxl_active_sheet.merged_cells:
                xlsxwriter_active_sheet.merge_range(merge_range.coord, "")
        return new_xlsx
