odoo.define('kpi_dashboard.NumberWidget', function (require) {
    "use strict";

    var IntegerWidget = require('kpi_dashboard.IntegerWidget');
    var registry = require('kpi_dashboard.widget_registry');
    var field_utils = require('web.field_utils');

    var NumberWidget = IntegerWidget.extend({
        digits: [3, 1],
        shortNumber: function (num) {
            if (Math.abs(num) < 10) {
                return field_utils.format.float(num, false, {
                    digits: [3, 2]});
            }
            return this._super.apply(this, arguments)
        },
    });

    registry.add('number', NumberWidget);
    return NumberWidget;
});
