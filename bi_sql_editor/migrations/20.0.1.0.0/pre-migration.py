# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version):
    # In 20.0, 'ir.rule' records have been converted into 'ir.access' records.
    # The ids stored in rule_id refer to the former 'ir.rule' table and must
    # not be interpreted as 'ir.access' ids. They are relinked in post-migration.
    cr.execute("UPDATE bi_sql_view SET rule_id = NULL")
