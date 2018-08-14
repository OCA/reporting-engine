# -*- coding: utf-8 -*-
# Copyright 2018 Simone Rubino - Agile Business Group
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from openupgradelib.openupgrade import logged_query, migrate
import json


@migrate()
def migrate(env, version):
    cr = env.cr
    convert_text_to_serialized(
        cr, env['bve.view']._table, env['bve.view']._fields['data'].name)
    pass


def convert_text_to_serialized(
        cr, table, text_field_name, serialized_field_name=None):
    """
    Convert Text field value to Serialized value.
    """
    if not serialized_field_name:
        serialized_field_name = text_field_name
    select_query = """
SELECT
    id,
    %(text_field_name)s
FROM %(table)s
WHERE %(text_field_name)s IS NOT NULL
"""
    cr.execute(
        select_query % {
            'text_field_name': text_field_name,
            'table': table,
        }
    )
    update_query = """
UPDATE %(table)s
    SET %(serialized_field_name)s = %%(field_value)s
    WHERE id = %(record_id)d
"""
    for row in cr.fetchall():
        # Fill in the field_value later because it needs escaping
        row_update_query = update_query % {
            'serialized_field_name': serialized_field_name,
            'table': table,
            'record_id': row[0]}
        logged_query(
            cr, row_update_query, {
                'field_value': json.dumps(row[1])
            })
