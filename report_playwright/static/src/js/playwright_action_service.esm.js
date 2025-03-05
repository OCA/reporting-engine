/** @odoo-module **/

import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";
import {user} from "@web/core/user";

function _getReportUrl(action, type, env) {
    let url = `/report/${type}/${action.report_name}`;
    const actionContext = action.context || {};
    if (action.data && JSON.stringify(action.data) !== "{}") {
        // Build a query string with `action.data` (it's the place where reports
        // using a wizard to customize the output traditionally put their options)
        const options = encodeURIComponent(JSON.stringify(action.data));
        const context = encodeURIComponent(JSON.stringify(actionContext));
        url += `?options=${options}&context=${context}`;
    } else {
        if (actionContext.active_ids) {
            url += `/${actionContext.active_ids.join(",")}`;
        }
        if (type === "html") {
            const context = encodeURIComponent(JSON.stringify(user.context));
            url += `?context=${context}`;
        }
    }
    return url;
}

async function _triggerDownload(env, action, options, type) {
    const url = _getReportUrl(action, type, env);
    env.services.ui.block();
    try {
        await download({
            url: "/report/download",
            data: {
                data: JSON.stringify([url, action.report_type]),
                context: JSON.stringify(user.context),
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
}

registry
    .category("ir.actions.report handlers")
    .add("playwright_handler", async function (action, options, env) {
        if (action.report_type === "playwright-pdf") {
            await _triggerDownload(env, action, options, "html");
            return Promise.resolve(true);
        }
        return Promise.resolve(false);
    });
