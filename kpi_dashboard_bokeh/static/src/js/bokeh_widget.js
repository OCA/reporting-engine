odoo.define('kpi_dashboard.BokehWidget', function (require) {
    "use strict";

    var AbstractWidget = require('kpi_dashboard.AbstractWidget');
    var registry = require('kpi_dashboard.widget_registry');


    var BokehWidget = AbstractWidget.extend({
        template: 'kpi_dashboard.bokeh',
        fillWidget: function (values) {
            var val = values.value.bokeh;
            var widget = this.$el.find('[data-bind="value"]');
            widget.css('height', this.widget_size_y - 90);
            widget.html(val);
        },
    });

    registry.add('bokeh', BokehWidget);
    return BokehWidget;
});
