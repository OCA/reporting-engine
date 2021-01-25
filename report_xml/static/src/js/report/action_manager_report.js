odoo.define("report_xml.ReportActionManager", function (require) {
    "use strict";

    var ActionManager = require("web.ActionManager");

    ActionManager.include({
        _executeReportAction: function (action, options) {
            if (action.report_type === "qweb-xml") {
                return this._triggerDownload(action, options, "xml");
            }
            return this._super(action, options);
        },
        _makeReportUrls: function (action) {
            var reportUrls = this._super(action);
            reportUrls.xml = reportUrls.text.replace("/report/text/", "/report/xml/");
            return reportUrls;
        },
    });
});
