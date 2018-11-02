// 2018 Hugo Rodrigues
// License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
odoo.define("report_controller.report", function(require){
"use strict";

var ActionManager = require("web.ActionManager");
var crash_manager = require("web.crash_manager");
var session = require("web.session");
var framework = require("web.framework");

var CONTROLLER_KEYS = ["controller"];

ActionManager.include({
    _triggerDownload: function (action, options, type) {
        // Since _downloadReport doesn't have the report type, we must
        // reimplement the method to be sure that is a controller report
        // without breaking other modules
        // If https://github.com/odoo/odoo/pull/28365 is merged and backported
        // into 12.0, we don't need to reimplement nothing.
        var self = this;
        if (!CONTROLLER_KEYS.includes(type)) {
            return self._super(action, options, type);
        }
        var reportUrls = self._makeReportUrls(action);
        framework.blockUI();
        var def = $.Deferred();
        var blocked = !session.get_file({
            url: "/report/download",
            data: {
                data: JSON.stringify([reportUrls[type], type]),
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
        return def.then(function () {
            if (action.close_on_report_download) {
                return self.doAction({type: "ir.actions.act_window_close"},
                                     _.pick(options, "on_close"));
            } else {
                return options.on_close();
            }
        });
    },

    _executeReportAction: function (action, options){
        var self = this;
        if (!CONTROLLER_KEYS.includes(action.report_type)) {
            return self._super(action, options);
        }
        return self._triggerDownload(action, options, action.report_type);
    },

    _makeReportUrls: function (action) {
        var self = this;
        var res = self._super(action);

        var reportUrls = {}

        $.each(CONTROLLER_KEYS, function(index, type) {
            reportUrls[type] = "/report/controller/" + action.report_name;
        });

        // Reimplement upstream url generation
        // check web/static/src/js/chrome/action_manager_report.js:180
        if (_.isUndefined(action.data) || _.isNull(action.data) ||
            (_.isObject(action.data) && _.isEmpty(action.data))) {
            if (action.context.active_ids) {
                var activeIDsPath = "/" + action.context.active_ids.join(',');
                _.mapObject(reportUrls, function (value, type) {
                    res[type] = value + activeIDsPath;
                });
            }
        } else {
            var serializedOptionsPath = '?options=' + encodeURIComponent(JSON.stringify(action.data));
            serializedOptionsPath += '&context=' + encodeURIComponent(JSON.stringify(action.context));
            _.mapObject(reportUrls, function (value, type) {
                res[type] = value + serializedOptionsPath;
            });
        }

        return res;
    }
});
});
