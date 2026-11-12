# Copyright 2025 Open Source Integrators
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields


def A(value, length=None):
    """
    Format as alphanumeric (A): left-aligned.

    Args:
        value: Value to format
        length: Fixed length for padding (optional)

    Returns:
        str: Formatted string
    """
    text = str(value or "")
    if length:
        text = text[:length]
        text = text.ljust(length)
    return text


def N(value, length=None, digits=None, sign=False):
    """
    Format as numeric (N): right-aligned with left zero padding.

    Args:
        value: Value to format
        length: Fixed length for padding (optional)
        digits: Number of decimal digits (optional)
        sign: Whether to include sign (+/-) at the end (optional)

    Returns:
        str: Formatted string
    """
    if value is None:
        value = 0

    # Handle decimal digits
    if digits is not None:
        # Multiply by 10^digits and round to get integer representation
        multiplier = 10**digits
        integer_value = int(round(abs(value) * multiplier))
        text = str(integer_value)
    else:
        text = str(abs(int(value)))

    # Apply padding (accounting for sign if requested)
    if length:
        padding_length = length - 1 if sign else length
        text = text.zfill(padding_length)[-padding_length:]

    # Add sign if requested (after padding)
    if sign:
        sign_char = "+" if value >= 0 else "-"
        text += sign_char

    return text


def M(value, length=None):
    """
    Format as monetary (M): calls N with default digits=2 and sign=True.

    Args:
        value: Value to format
        length: Fixed length for padding (optional)

    Returns:
        str: Formatted string
    """
    return N(value, length, digits=2, sign=True)


def T(value, length=5, digits=2):
    # Tax: number with two decimals and no sign
    return N(value, length, digits=digits, sign=False)


def DT(value, length=12, dtformat="%Y%m%d%H%M"):
    """
    Format as datetime (DT): formats datetime values with customizable format.

    Args:
        value: Datetime value to format
        length: Fixed length for padding (default: 12 for yyyyMMddhhmm)
        dtformat: Datetime format string (default: "%Y%m%d%H%M")

    Returns:
        str: Formatted datetime string
    """
    if not value:
        value = fields.Datetime.now()
    text = value.strftime(dtformat) if value else ""
    return A(text, length)


def D(value, length=8, dtformat="%Y%m%d"):
    # Format as date yyymmdd
    return DT(value, length=length, dtformat=dtformat)


def H(value, length=4, dtformat="%H%M"):
    # Format as hour 24h format HHMM
    return DT(value, length=length, dtformat=dtformat)
