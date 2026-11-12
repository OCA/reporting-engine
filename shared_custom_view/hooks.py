def pre_init_hook(env):
    env.ref("base.ir_ui_view_custom_personal", raise_if_not_found=True).write(
        {"domain_force": "['|', ('user_id','=',user.id), ('user_id', '=', False)]"}
    )
