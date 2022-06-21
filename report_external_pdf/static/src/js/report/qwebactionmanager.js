// (Copyright) 2017-2020 Creu Blanca
// License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
/* global _t */
odoo.define("report_external_pdf.report", function(require) {
    "use strict";

    var ActionManager = require("web.ActionManager");
    var session = require("web.session");
    var framework = require("web.framework");

    ActionManager.include({
        _executeReportAction: function(action, options) {
            var self = this;
            if (action.report_type === "external_pdf") {
                return self._triggerDownload(action, options, "external_pdf");
            }
            return this._super.apply(this, arguments);
        },
        _makeReportUrls: function(action) {
            var reportUrls = this._super.apply(this, arguments);
            reportUrls.external_pdf = "/report/external_pdf/" + action.report_name;
            return reportUrls;
        },
        _triggerDownload: function(action, options, type) {
            var self = this;
            var reportUrls = this._makeReportUrls(action);
            if (type === "external_pdf") {
                return this._downloadReportExternalPdf(reportUrls[type], action).then(
                    function() {
                        if (action.close_on_report_download) {
                            var closeAction = {type: "ir.actions.act_window_close"};
                            return self.doAction(
                                closeAction,
                                _.pick(options, "on_close")
                            );
                        }
                        return options.on_close();
                    }
                );
            }
            return this._super.apply(this, arguments);
        },
        _downloadReportExternalPdf: function(url, actions) {
            var self = this;
            framework.blockUI();
            var type = "external_pdf";
            var cloned_action = _.clone(actions);
            var report_url = url;

            if (
                _.isUndefined(cloned_action.data) ||
                _.isNull(cloned_action.data) ||
                (_.isObject(cloned_action.data) && _.isEmpty(cloned_action.data))
            ) {
                if (cloned_action.context.active_ids) {
                    report_url += "/" + cloned_action.context.active_ids.join(",");
                }
            } else {
                report_url +=
                    "?options=" +
                    encodeURIComponent(JSON.stringify(cloned_action.data));
                report_url +=
                    "&context=" +
                    encodeURIComponent(JSON.stringify(cloned_action.context));
            }

            return new Promise(function(resolve, reject) {
                var blocked = !session.get_file({
                    url: report_url,
                    data: {
                        data: JSON.stringify([report_url, type]),
                    },
                    success: resolve,
                    error: error => {
                        self.call("crash_manager", "rpc_error", error);
                        reject();
                    },
                    complete: framework.unblockUI,
                });
                if (blocked) {
                    // AAB: this check should be done in get_file service directly,
                    // should not be the concern of the caller (and that way, get_file
                    // could return a deferred)
                    var message = _t(
                        "A popup window with your report was blocked. You " +
                            "may need to change your browser settings to allow " +
                            "popup windows for this page."
                    );
                    this.do_warn(_t("Warning"), message, true);
                }
            });
        },
    });
});
