# Copyright 2021 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from openupgradelib.openupgrade import rename_xmlids


def migrate(cr, version):

    rename_xmlids(
        cr,
        [
            (
                "report_layout_config.external_layout_images",
                "report_layout_config.external_standard_layout_images_template",
            )
        ],
    )
