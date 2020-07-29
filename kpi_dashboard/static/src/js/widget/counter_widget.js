odoo.define('kpi_dashboard.CounterWidget', function (require) {
    "use strict";

    var IntegerWidget = require('kpi_dashboard.IntegerWidget');
    var registry = require('kpi_dashboard.widget_registry');
    var field_utils = require('web.field_utils');

    var CounterWidget = IntegerWidget.extend({
        shortList: [],
    });

    registry.add('counter', CounterWidget);
    return CounterWidget;
});
