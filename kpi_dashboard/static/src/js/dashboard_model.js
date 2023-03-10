odoo.define("kpi_dashboard.DashboardModel", function (require) {
    "use strict";

    var BasicModel = require("web.BasicModel");

    var DashboardModel = BasicModel.extend({
        _fetchRecord: function (record, options) {
            var self = this;
            return this._rpc({
                model: record.model,
                method: "read_dashboard",
                args: [[record.res_id]],
                context: _.extend({}, record.getContext(), {bin_size: true}),
            })
                .then(function (result) {
                    record.specialData = result;
                })
                .then(function () {
                    return self._postprocess(record, options);
                });
        },
    });

    return DashboardModel;
});
