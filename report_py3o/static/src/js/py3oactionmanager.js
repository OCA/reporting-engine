/* Copyright 2017 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define('report_py3o.report', function (require) {

var ActionManager = require('web.ActionManager');
var core = require('web.core');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');
var session = require('web.session');

var _t = core._t;

var trigger_download = function(session, response, c, action, options) {
    session.get_file({
        url: '/report/download',
        data: {data: JSON.stringify(response)},
        complete: framework.unblockUI,
        error: c.rpc_error.bind(c),
        success: function(){
            if (action && options && !action.dialog) {
                options.on_close();
            }
        },
    });
};

ActionManager.include({
    _executeReportAction: function (action, options) {
        // Py3o reports
        if ('report_type' in action && action.report_type === 'py3o' ) {
            return this._triggerDownload(action, options, 'py3o');
        } else {
            return this._super.apply(this, arguments);
        }
    },

    _makeReportUrls: function(action) {
        var reportUrls = this._super.apply(this, arguments);
        reportUrls.py3o = '/report/py3o/' + action.report_name;
        // We may have to build a query string with `action.data`. It's the place
        // were report's using a wizard to customize the output traditionally put
        // their options.
        if (_.isUndefined(action.data) || _.isNull(action.data) ||
            (_.isObject(action.data) && _.isEmpty(action.data))) {
            if (action.context.active_ids) {
                var activeIDsPath = '/' + action.context.active_ids.join(',');
                reportUrls.py3o += activeIDsPath;;
            }
        } else {
            var serializedOptionsPath = '?options=' + encodeURIComponent(JSON.stringify(action.data));
            serializedOptionsPath += '&context=' + encodeURIComponent(JSON.stringify(action.context));
            reportUrls.py3o += serializedOptionsPath;
        }
        return reportUrls;
    }
});

});
