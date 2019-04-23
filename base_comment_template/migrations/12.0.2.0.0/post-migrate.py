from odoo import tools

import logging
_logger = logging.getLogger(__name__)


def migrate(cr, version):

    _logger.debug('Migrating res.partner comment_template_id')

    if not tools.column_exists(cr, 'res_partner', 'comment_template_id'):
        return

    cr.execute("SELECT id FROM res_company")
    company_ids = [d[0] for d in cr.fetchall()]

    cr.execute(
        "SELECT id FROM ir_model_fields WHERE model=%s AND name=%s",
        ('res.partner', 'property_comment_template_id'))
    [field_id] = cr.fetchone()

    for company_id in company_ids:
        cr.execute("""
            INSERT INTO ir_property(
                name,
                type,
                fields_id,
                company_id,
                res_id,
                value_reference
            )
            SELECT
                {field},
                'many2one',
                {field_id},
                {company_id},
                CONCAT('{model},',id),
                CONCAT('{target_model},',{oldfield})
            FROM {table} t
            WHERE {oldfield} IS NOT NULL
            AND (company_id IS NULL OR company_id = {company_id})
            AND NOT EXISTS(
                SELECT 1
                FROM ir_property
                WHERE fields_id={field_id}
                AND company_id={company_id}
                AND res_id=CONCAT('{model},',t.id)
            )
        """.format(
            oldfield='comment_template_id',
            field='property_comment_template_id',
            field_id=field_id,
            company_id=company_id,
            model='res.partner',
            target_model='base.comment.template',
            table='res_partner',
        ))
