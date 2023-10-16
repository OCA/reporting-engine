# Copyright 2023 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import logging

import xlsxwriter

from odoo.exceptions import ValidationError

from odoo.addons.report_xlsx.tests.test_report import TestReport

_logger = logging.getLogger(__name__)


class TestReportXlsxBoilerplate(TestReport):
    def setUp(self):
        super().setUp()

    def test_01_boilerplate_template_usage(self):
        """
        Test to get the Boilerplate Template, and check its values
        """
        # Define Boilerplate Template path
        self.xlsx_report._boilerplate_template_file_path = (
            "tests/sample_files/test_partner_report_boilerplate_template.xlsx"
        )
        workbook = self.xlsx_report._get_boilerplate_template(self.docs.ids)
        sheet_names = ["Test Sheet 1", "Test Sheet 2"]
        cell_str_tup_obj = xlsxwriter.worksheet.cell_string_tuple
        for count, sheet_name in enumerate(sheet_names):
            worksheet = workbook.get_worksheet_by_name(sheet_name)
            self.assertTrue(worksheet, "The sheet should exist.")
            cell_1 = worksheet.table.get(0, dict()).get(0, dict())
            if cell_1 and isinstance(cell_1, cell_str_tup_obj):
                cell_1_string = cell_1[0]
                cell_1_format = cell_1[1]
            cell_2 = worksheet.table.get(3, dict()).get(0, dict())
            if cell_2 and isinstance(cell_2, cell_str_tup_obj):
                cell_2_string = cell_2[0]
                cell_2_format = cell_2[1]
            shared_strings = sorted(
                worksheet.str_table.string_table,
                key=worksheet.str_table.string_table.get,
            )
            if count == 0:
                # Test Sheet 1
                self.assertTrue(cell_1, "Cell 1 should exist in sheet 1.")
                self.assertFalse(cell_2, "Cell 2 should not exist in sheet 1.")
                if isinstance(cell_1, cell_str_tup_obj):
                    cell_1_string_val = shared_strings[cell_1_string]
                    self.assertEqual(
                        cell_1_string_val,
                        "Test Partner\nTest Enter",
                        "The value of the cell of sheet 1 does not match.",
                    )
                self.assertTrue(cell_1_format.bold, "Cell should contain bold text.")
                self.assertTrue(
                    cell_1_format.italic, "Cell should contain italic text."
                )
                self.assertTrue(
                    cell_1_format.underline, "Cell should contain underlined text."
                )
                self.assertTrue(
                    cell_1_format.text_wrap, "Cell should contain wrapped text."
                )
                self.assertEqual(cell_1_format.font_color, "#000000")
                self.assertEqual(cell_1_format.bg_color, "#FFFF00")
                # Hardcoded values here as XlsxWriter Format class doesn't hold the
                # 'string' values
                self.assertEqual(cell_1_format.text_h_align, 2)
                self.assertEqual(cell_1_format.text_v_align, 3)
            else:
                # Test Sheet 2
                self.assertTrue(cell_1, "Cell 1 should exist in sheet 2.")
                self.assertTrue(cell_2, "Cell 2 should exist in sheet 2.")
                if isinstance(cell_1, cell_str_tup_obj):
                    cell_1_string_val = shared_strings[cell_1_string]
                    self.assertEqual(
                        cell_1_string_val,
                        "",
                        "The content of the 0, 0 cell of sheet 2 should be empty.",
                    )
                if isinstance(cell_2, cell_str_tup_obj):
                    cell_2_string_val = shared_strings[cell_2_string]
                    self.assertEqual(
                        cell_2_string_val,
                        "Testing for sheet 2",
                        "The value of the cell 3,0 of sheet 2 does not match.",
                    )
                # Hardcoded values here as XlsxWriter Format class doesn't hold the
                # 'string' values
                self.assertEqual(cell_2_format.text_h_align, 1)
                self.assertEqual(cell_2_format.text_v_align, 1)

    def test_02_boilerplate_template_wrong_path(self):
        """
        Check that ValidationError is raised when the path is wrongly formated.
        """
        self.xlsx_report._boilerplate_template_file_path = (
            "wrong_path/wrong_path_file.xlsx"
        )
        with self.assertRaises(ValidationError):
            self.xlsx_report._get_boilerplate_template(self.docs.ids)
