/* Copyright 2017-2018 ACSONE SA/NV
 * License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl). */
odoo.define('report_py3o.report', function (require) {

var ActionManager = require('web.ActionManager');
var crash_manager = require('web.crash_manager');
var framework = require('web.framework');


ActionManager.include({
	ir_actions_report: function (action, options) {
        // Py3o reports
		var self = this;
		var cloned_action = _.clone(action);
        if (cloned_action.report_type === 'py3o' ) {
        	framework.blockUI();
        	 var report_py3o_url = '/report/py3o/' + cloned_action.report_name;
        	 if (_.isUndefined(cloned_action.data) || _.isNull(cloned_action.data) ||
        	            (_.isObject(cloned_action.data) && _.isEmpty(cloned_action.data))) {
        	            if (cloned_action.context.active_ids) {
        	            	report_py3o_url += '/' + cloned_action.context.active_ids.join(',');
        	            }
        	         else {
        	            report_py3o_url += '?options=' + encodeURIComponent(JSON.stringify(cloned_action.data));
        	            report_py3o_url += '&context=' + encodeURIComponent(JSON.stringify(cloned_action.context));
        	        }
        	 }
        	 self.getSession().get_file({
                 url: report_py3o_url,
                 data: {data: JSON.stringify([
                	 report_py3o_url,
                     cloned_action.report_type
                 ])},
                 error: crash_manager.rpc_error.bind(crash_manager),
                 success: function (){
                     if(cloned_action && options && !cloned_action.dialog){
                         options.on_close();
                     }
                 }
             });
             framework.unblockUI();
             return;
        }
        return self._super(action, options);

	  }
});
});
