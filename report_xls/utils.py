# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#
#    Copyright (c) 2014 Noviat nv/sa (www.noviat.com). All rights reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################


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

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
