// © 2019 Creu Blanca
// License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
odoo.define("report_csv.report", function(require) {
    "use strict";

    var core = require("web.core");
    var ActionManager = require("web.ActionManager");
    var framework = require("web.framework");
    var session = require("web.session");
    var _t = core._t;

    ActionManager.include({
        _downloadReportCSV: function(url, actions) {
            var self = this;
            framework.blockUI();
            var type = "csv";
            var cloned_action = _.clone(actions);

            if (
                _.isUndefined(cloned_action.data) ||
                _.isNull(cloned_action.data) ||
                (_.isObject(cloned_action.data) && _.isEmpty(cloned_action.data))
            ) {
                if (cloned_action.context.active_ids) {
                    url += "/" + cloned_action.context.active_ids.join(",");
                }
            } else {
                url +=
                    "?options=" +
                    encodeURIComponent(JSON.stringify(cloned_action.data));
                url +=
                    "&context=" +
                    encodeURIComponent(JSON.stringify(cloned_action.context));
            }

            return new Promise(function(resolve, reject) {
                var blocked = !session.get_file({
                    url: url,
                    data: {
                        data: JSON.stringify([url, type]),
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

        _triggerDownload: function(action, options, type) {
            var self = this;
            var reportUrls = this._makeReportUrls(action);
            if (type === "csv") {
                return this._downloadReportCSV(reportUrls[type], action).then(
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

        _makeReportUrls: function(action) {
            var reportUrls = this._super.apply(this, arguments);
            reportUrls.csv = "/report/csv/" + action.report_name;
            return reportUrls;
        },

        _executeReportAction: function(action, options) {
            var self = this;
            if (action.report_type === "csv") {
                return self._triggerDownload(action, options, "csv");
            }
            return this._super.apply(this, arguments);
        },
    });
});
