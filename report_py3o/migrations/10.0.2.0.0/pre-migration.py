# © 2018 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def migrate(cr, version=None):
    # when migrating from a pre-split version of the module, pull the fusion
    # server module too to have no loss of features
    cr.execute(
        "update ir_module_module set state='to install' "
        "where name='report_py3o_fusion_server' and state='uninstalled'"
    )
