# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).


from odoo.tests import TransactionCase, tagged

from ..report import field_formatter


@tagged("-at_install", "post_install")
class TestFieldFormatter(TransactionCase):
    """Test field formatting functions."""

    def test_alphanumeric_formatter(self):
        """Test alphanumeric field formatting."""
        self.assertEqual(field_formatter.A(None, 5), "     ")
        self.assertEqual(field_formatter.A(123, 5), "123  ")
        self.assertEqual(field_formatter.A("Test", 10), "Test      ")
        self.assertEqual(field_formatter.A("LongerText", 5), "Longe")

    def test_numeric_formatter(self):
        """Test numeric field formatting."""
        # Test basic formatting
        self.assertEqual(field_formatter.N(None), "0")
        self.assertEqual(field_formatter.N(123), "123")
        self.assertEqual(field_formatter.N(123, 8), "00000123")
        self.assertEqual(field_formatter.N(123.45, 8), "00000123")

        # Test with digits parameter
        self.assertEqual(field_formatter.N(123.456, 8, digits=2), "00012346")
        self.assertEqual(field_formatter.N(123.456, 8, digits=3), "00123456")

        # Test with sign parameter
        self.assertEqual(field_formatter.N(123, 8, sign=True), "0000123+")
        self.assertEqual(field_formatter.N(-123, 8, sign=True), "0000123-")
        self.assertEqual(field_formatter.N(-123, 8, sign=False), "00000123")

        # Test edge cases
        self.assertEqual(field_formatter.N(-123, 8, sign=True), "0000123-")
        self.assertEqual(field_formatter.N(0, 5), "00000")

    def test_monetary_formatter(self):
        """Test monetary field formatting."""
        # Test basic formatting
        self.assertEqual(field_formatter.M(100.50, 10), "000010050+")
        self.assertEqual(field_formatter.M(-100.50, 10), "000010050-")
        self.assertEqual(field_formatter.M(0, 8), "0000000+")

        # Test with None length
        self.assertEqual(field_formatter.M(100.50), "10050+")

        # Test rounding
        self.assertEqual(field_formatter.M(100.456, 10), "000010046+")
        self.assertEqual(field_formatter.M(100.454, 10), "000010045+")

    def test_date_formatter(self):
        """Test date field formatting."""
        from datetime import date, datetime

        # Test with datetime object
        dt = datetime(2025, 1, 15, 10, 30, 45)
        self.assertEqual(field_formatter.D(dt), "20250115")

        # Test with date object
        d = date(2025, 1, 15)
        self.assertEqual(field_formatter.D(d), "20250115")

        # Test with custom format
        self.assertEqual(field_formatter.D(dt, 10, dtformat="%Y-%m-%d"), "2025-01-15")
        self.assertEqual(field_formatter.D(dt, 10, dtformat="%d/%m/%Y"), "15/01/2025")

        # Test with None - should use current datetime and format as date
        from odoo import fields

        current_dt = fields.Datetime.now()
        expected_current_date = current_dt.strftime("%Y%m%d")
        self.assertEqual(field_formatter.D(None, None), expected_current_date)

        # Test with length
        self.assertEqual(field_formatter.D(dt, 12), "20250115    ")
        self.assertEqual(field_formatter.D(dt, 12, dtformat="%Y-%m-%d"), "2025-01-15  ")

    def test_H_formatter(self):
        """Test H field formatting (time)."""
        from datetime import datetime, time

        # Test with datetime object
        dt = datetime(2025, 1, 15, 14, 30, 45)
        self.assertEqual(field_formatter.H(dt), "1430")

        # Test with time object
        t = time(14, 30, 45)
        self.assertEqual(field_formatter.H(t), "1430")

        # Test with custom format
        self.assertEqual(field_formatter.H(dt, 5, dtformat="%H:%M"), "14:30")
        self.assertEqual(field_formatter.H(dt, None, dtformat="%I:%M %p"), "02:30 PM")

        # Test with None - should use current datetime and format as time
        from odoo import fields

        current_dt = fields.Datetime.now()
        expected_current_time = current_dt.strftime("%H%M")
        self.assertEqual(field_formatter.H(None), expected_current_time)

        # Test with length
        self.assertEqual(field_formatter.H(dt, 6), "1430  ")
        self.assertEqual(field_formatter.H(dt, 8, dtformat="%H:%M:%S"), "14:30:45")

    def test_T_formatter(self):
        """Test T field formatting (tax)."""
        # Test basic tax formatting without sign (default length=5, digits=2)
        self.assertEqual(field_formatter.T(123.45), "12345")
        self.assertEqual(field_formatter.T(0), "00000")
        self.assertEqual(field_formatter.T(-123.45), "12345")  # No sign

        # Test with explicit length
        self.assertEqual(field_formatter.T(123.45, 6), "012345")

        # Test with custom digits
        self.assertEqual(field_formatter.T(23.456, digits=3), "23456")
        self.assertEqual(field_formatter.T(123.45, digits=0), "00123")

        # Test with None
        self.assertEqual(field_formatter.T(None), "00000")

    def test_datetime_formatter(self):
        """Test datetime field formatting."""
        from datetime import datetime

        # Test with datetime object
        dt = datetime(2025, 1, 15, 14, 30, 45)
        self.assertEqual(field_formatter.DT(dt), "202501151430")

        # Test with custom format
        self.assertEqual(
            field_formatter.DT(dt, None, dtformat="%Y-%m-%d %H:%M"), "2025-01-15 14:30"
        )
        self.assertEqual(
            field_formatter.DT(dt, None, dtformat="%Y%m%d_%H%M%S"), "20250115_143045"
        )

        # Test with None - should use current datetime
        from odoo import fields

        current_dt = fields.Datetime.now()
        expected_current = current_dt.strftime("%Y%m%d%H%M")
        self.assertEqual(field_formatter.DT(None), expected_current)
        self.assertEqual(field_formatter.DT(None, None), expected_current)

        # Test with length
        self.assertEqual(field_formatter.DT(dt, 16), "202501151430    ")
        self.assertEqual(
            field_formatter.DT(dt, 19, dtformat="%Y-%m-%d %H:%M:%S"),
            "2025-01-15 14:30:45",
        )
