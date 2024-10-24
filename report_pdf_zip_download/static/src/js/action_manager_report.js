// © 2017 Creu Blanca
// Copyright 2024 Quartile (https://www.quartile.co)
// License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
odoo.define("report_pdf_zip_download.report", function (require) {
    "use strict";

    var core = require("web.core");
    var ActionManager = require("web.ActionManager");
    var crash_manager = require("web.crash_manager");
    var framework = require("web.framework");
    var session = require("web.session");
    var _t = core._t;

    ActionManager.include({

        _downloadReportZIP: function (url, actions) {
            framework.blockUI();
            var def = $.Deferred();
            var type = "zip";
            var cloned_action = _.clone(actions);

            if (_.isUndefined(cloned_action.data) ||
                _.isNull(cloned_action.data) ||
                (_.isObject(cloned_action.data) && _.isEmpty(cloned_action.data)))
            {
                if (cloned_action.context.active_ids) {
                    url += "/" + cloned_action.context.active_ids.join(',');
                }
            } else {
                url += "?options=" + encodeURIComponent(JSON.stringify(cloned_action.data));
                url += "&context=" + encodeURIComponent(JSON.stringify(cloned_action.context));
            }

            var blocked = !session.get_file({
                url: url,
                data: {
                    data: JSON.stringify([url, type]),
                },
                success: def.resolve.bind(def),
                error: function () {
                    crash_manager.rpc_error.apply(crash_manager, arguments);
                    def.reject();
                },
                complete: framework.unblockUI,
            });
            if (blocked) {
                var message = _t('A popup window with your report was blocked. You ' +
                                 'may need to change your browser settings to allow ' +
                                 'popup windows for this page.');
                this.do_warn(_t('Warning'), message, true);
            }
            return def;
        },

        _triggerDownload: function (action, options, type) {
            var self = this;
            var reportUrls = this._makeReportUrls(action);
            if (type === "zip") {
                return this._downloadReportZIP(reportUrls[type], action).then(function () {
                    if (action.close_on_report_download) {
                        var closeAction = {type: 'ir.actions.act_window_close'};
                        return self.doAction(closeAction, _.pick(options, 'on_close'));
                    } else {
                        return options.on_close();
                    }
                });
            }
            return this._super.apply(this, arguments);
        },

        _makeReportUrls: function (action) {
            var reportUrls = this._super.apply(this, arguments);
            reportUrls.zip = '/report/zip/' + action.report_name;
            return reportUrls;
        },

        _executeReportAction: function (action, options) {
            var self = this;
        
            console.log(action.data);
            console.log(action.context);
            if (action.context.active_ids && action.context.active_ids.length > 1) {
                if (action.report_type === 'qweb-pdf' && action.zip_download === true) {
                    return self._triggerDownload(action, options, 'zip');
                }
            }
            return this._super.apply(this, arguments);
        }
    });

});
