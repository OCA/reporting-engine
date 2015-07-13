/*Code inspired in OPENERP S.A report module */

openerp.report_xls_template = function(instance) {

    var trigger_download = function(session, response, c) {
        session.get_file({
            url: '/reportxlstemplate/download',
            data: {data: JSON.stringify(response)},
            complete: openerp.web.unblockUI,
            error: c.rpc_error.bind(c)
        });
    }

    instance.web.ActionManager = instance.web.ActionManager.extend({
        ir_actions_report_xml: function(action, options) {
            var self = this;
            instance.web.blockUI();
            action = _.clone(action);
            _t =  instance.web._t;

            // XLS reports
            if ('report_type' in action && (action.report_type == 'qweb-xls' || action.report_type == 'qweb-ods')) {
                var report_url = '';
                switch (action.report_type) {
                    case 'qweb-xls':
                        report_url = '/reportxlstemplate/xls/' + action.report_name;
                        break;
                    case 'qweb-ods':
                        report_url = '/reportxlstemplate/ods/' + action.report_name;
                        break;
                    default:
                        report_url = '/reportxlstemplate/xls/' + action.report_name;
                        break;
                }

                // generic report: no query string
                // particular: query string of action.data.form and context
                if (!('data' in action) || !(action.data)) {
                    if ('active_ids' in action.context) {
                        report_url += "/" + action.context.active_ids.join(',');
                    }
                } else {
                    report_url += "?options=" + encodeURIComponent(JSON.stringify(action.data));
                    report_url += "&context=" + encodeURIComponent(JSON.stringify(action.context));
                }

                var response = new Array();
                response[0] = report_url;
                response[1] = action.report_type;
                var c = openerp.webclient.crashmanager;

                if (action.report_type === 'qweb-xls') {
                    return trigger_download(self.session, response, c);
                }
            } else {
                return self._super(action, options);
            }
        }
    });
};
