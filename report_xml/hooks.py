# License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).

import os

from odoo import SUPERUSER_ID, api


def post_init_hook(cr, registry):
    """
    Loaded after installing this module, and before the next module starts
    installing.

    Add XSD Validation Schema for a demo report if it's in the system.
    Demo data records are always created with `noupdate == True` and render of
    tag `report` doesn't support new `ir.actions.report` field `xsd_schema`.
    Thus it is impossible to define `xsd_schema` in the demo definition or add
    schema after that via xml update record. Therefore it possible to add value
    to `xsd_schema` field for demo record only via hook.

    Args:
     * cr(odoo.sql_db.Cursor) - database cursor.
     * registry(odoo.modules.registry.RegistryManager) - a mapping between
     model names and model classes.
    """
    env = api.Environment(cr, SUPERUSER_ID, {})
    report_domain = [
        ("report_name", "=", "report_xml.demo_report_xml_view")  # report tech name
    ]
    demo_report = env["ir.actions.report"].search(report_domain, limit=1)
    if demo_report:
        dir_path = os.path.dirname(__file__)
        xsd_file_relative_path = "demo/demo_report.xsd"
        xsd_file_full_path = os.path.join(dir_path, xsd_file_relative_path)

        with open(xsd_file_full_path, "r") as xsd:
            # `xsd_schema` is binary fields with an attribute
            # `attachment=True` so XSD Schema will be added as attachment
            attach_vals = {
                "name": "Demo Report.xsd",
                "datas": xsd.read(),
                "res_model": "ir.actions.report",
                "res_id": demo_report.id,
                "res_field": "xsd_schema",
                "type": "binary",
            }
            env["ir.attachment"].create(attach_vals)
