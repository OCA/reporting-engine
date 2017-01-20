# -*- encoding: utf-8 -*-
# Copyright 2014 Noviat nv/sa (<http://www.noviat.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def _render(code):
    return compile(code, '<string>', 'eval')


def rowcol_to_cell(row, col, row_abs=False, col_abs=False):
    # Code based upon utils from xlwt distribution
    """
    Convert numeric row/col notation to an Excel cell
    reference string in A1 notation.
    """
    d = col // 26
    m = col % 26
    chr1 = ""    # Most significant character in AA1
    if row_abs:
        row_abs = '$'
    else:
        row_abs = ''
    if col_abs:
        col_abs = '$'
    else:
        col_abs = ''
    if d > 0:
        chr1 = chr(ord('A') + d - 1)
    chr2 = chr(ord('A') + m)
    # Zero index to 1-index
    return col_abs + chr1 + chr2 + row_abs + str(row + 1)

