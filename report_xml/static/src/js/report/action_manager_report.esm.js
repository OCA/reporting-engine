/** @odoo-module **/

import {download} from "@web/core/network/download";
import {registry} from "@web/core/registry";

async function xmlReportHandler(action, options, env) {
    if (action.report_type === "qweb-xml") {
        // Workaround/hack: Odoo does not expose the _triggerDownload method on
        // the service, so we have no way to access it from here. We therefore
        // copy the code; as it is private, it doesn't really give any
        // stability guarantees anyway
        // If _triggerDownload were publically available on the service, the
        // code below could be replaced by
        // env.services.action._triggerDownload(action, options, "xml");

        const type = "xml";
        // COPY actionManager._getReportUrl
        let url_ = `/report/${type}/${action.report_name}`;
        const actionContext = action.context || {};
        if (action.data && JSON.stringify(action.data) !== "{}") {
            // Build a query string with `action.data` (it's the place where reports
            // using a wizard to customize the output traditionally put their options)
            const options_ = encodeURIComponent(JSON.stringify(action.data));
            const context_ = encodeURIComponent(JSON.stringify(actionContext));
            url_ += `?options=${options_}&context=${context_}`;
        } else {
            if (actionContext.active_ids) {
                url_ += `/${actionContext.active_ids.join(",")}`;
            }
            if (type === "xml") {
                const context = encodeURIComponent(
                    JSON.stringify(env.services.user.context)
                );
                url_ += `?context=${context}`;
            }
        }
        // COPY actionManager._triggerDownload
        env.services.ui.block();
        try {
            await download({
                url: "/report/download",
                data: {
                    data: JSON.stringify([url_, action.report_type]),
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
        // DIFF: need to inform success to the original method. Otherwise it
        // will think our hook function did nothing and run the original
        // method.
        return Promise.resolve(true);
    }
}

registry.category("ir.actions.report handlers").add("xml_handler", xmlReportHandler);
