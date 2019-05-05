/* Copyright 2017-2018 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */

 odoo.define('report_py3o.report', function (require) {
'use strict';

    var ActionManager = require('web.ActionManager');
    var crash_manager = require('web.crash_manager');
    var framework = require('web.framework');

    
    var trigger_download = function (session, response, c, action, options) {
        return session.get_file({
            url: '/report/download',
            data: {data: JSON.stringify(response)},
            complete: framework.unblockUI,
            error: c.rpc_error.bind(c),
            success: function () {
                if (action && options && !action.dialog) {
                    options.on_close();
                }
            },
        });
    };
    
    var make_report_url = function (action) {
        var report_urls = {
            'py3o': '/report/py3o/' + action.report_name,
        };
        // We may have to build a query string with `action.data`. It's the place
        // were report's using a wizard to customize the output traditionally put
        // their options.
        if (_.isUndefined(action.data) || _.isNull(action.data) ||
            (_.isObject(action.data) && _.isEmpty(action.data))) {
            if (action.context.active_ids) {
                var activeIDsPath = '/' + action.context.active_ids.join(',');
                // Update the report's type - report's url mapping.
                report_urls = _.mapObject(report_urls, function (value, key) {
                    return value += activeIDsPath;
                });
            }
        } else {
            var serialized_options_path = '?options=' + encodeURIComponent(JSON.stringify(action.data));
            serialized_options_path += '&context=' + encodeURIComponent(JSON.stringify(action.context));
            // Update the report's type - report's url mapping.
            report_urls = _.mapObject(report_urls, function (value, key) {
                return value += serialized_options_path;
            });
        }
        return report_urls;
    };
    
    ActionManager.include({
        ir_actions_report: function (action, options) {
            var self = this;
            action = _.clone(action);
    
            var report_urls = make_report_url(action);
            var current_action = action;
            var c = crash_manager;
            var response = [
                report_urls['py3o'],
                action.report_type, //The 'root' report is considered the maine one, so we use its type for all the others.
            ];
            // Py3o reports
            if ('report_type' in action && action.report_type === 'py3o' ) {
                return trigger_download(self.getSession(), response, c, current_action, options);
            } else {
                return this._super.apply(this, arguments);
            }
        }
    });
    
    });
