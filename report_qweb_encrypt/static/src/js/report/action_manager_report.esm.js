/** @odoo-module **/

import {Dialog} from "@web/core/dialog/dialog";
import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";

async function download_function(action, options, env) {
    const type = action.report_type;
    let url = `/report/${type}/${action.report_name}`;
    const actionContext = action.context || {};
    if (action.data && JSON.stringify(action.data) !== "{}") {
        // Build a query string with `action.data` (it's the place where reports
        // using a wizard to customize the output traditionally put their options)
        const action_options = encodeURIComponent(JSON.stringify(action.data));
        const context = encodeURIComponent(JSON.stringify(actionContext));
        url += `?options=${action_options}&context=${context}`;
    } else {
        if (actionContext.active_ids) {
            url += `/${actionContext.active_ids.join(",")}`;
        }
        if (type === "html") {
            const context = encodeURIComponent(
                JSON.stringify(env.services.user.context)
            );
            url += `?context=${context}`;
        }
    }
    env.services.ui.block();
    try {
        await download({
            url: "/report/download",
            data: {
                data: JSON.stringify([url, action.report_type]),
                context: JSON.stringify(env.services.user.context),
            },
        });
    } finally {
        env.services.ui.unblock();
    }
    const onClose = options.onClose;
    if (action.close_on_report_download) {
        return env.services.action.doAction(
            {type: "ir.actions.act_window_close"},
            {onClose}
        );
    } else if (onClose) {
        onClose();
    }
    return Promise.resolve(true);
}

class EncryptDialog extends Dialog {
    onClick() {
        const action = this.props.action;
        action.context = _.extend({}, action.context, {
            encrypt_password: this.el.find(".o_password").val() || false,
        });
        return download_function(action, this.props.options, this.props.env);
    }
}
EncryptDialog.size = "small";
EncryptDialog.title = "Encrypt";
EncryptDialog.bodyTemplate = "report_qweb_encrypt.EncryptDialogBody";
EncryptDialog.footerTemplate = "report_qweb_encrypt.EncryptDialogFooter";

registry
    .category("ir.actions.report handlers")
    .add("qweb-pdf-password", async function (action, options, env) {
        if (action.encrypt === "manual" && action.report_type === "qweb-pdf") {
            return env.services.dialog.add(EncryptDialog, {
                action: action,
                options: options,
                env: env,
            });
        }
        return Promise.resolve(false);
    });
