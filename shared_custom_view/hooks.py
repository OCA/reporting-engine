from odoo import SUPERUSER_ID, api


def pre_init_hook(cr):
    env = api.Environment(cr, SUPERUSER_ID, {})
    env.ref("base.ir_ui_view_custom_personal", raise_if_not_found=True).write(
        {"domain_force": "['|', ('user_id','=',user.id), ('user_id', '=', False)]"}
    )
