odoo.define('kpi_dashboard.AltairWidget', function (require) {
    "use strict";

    var AbstractWidget = require('kpi_dashboard.AbstractWidget');
    var registry = require('kpi_dashboard.widget_registry');

    var AltairWidget = AbstractWidget.extend({
        template: 'kpi_dashboard.altair',
        fillWidget: function (values) {
            var widget = this.$el.find('[data-bind="value"]');
            widget.css('width', this.widget_size_x-20);
            widget.css('height', this.widget_size_y-90);
            var data = $.extend({
                height: this.widget_size_y - 90,
                width: this.widget_size_x - 20,
                autosize: {
                    type: "fit",
                    contains: "padding"
                },
            }, values.value.altair);
            vegaEmbed(
                widget[0],
                data,
                this.altairOptions(values)
            );
        },
        altairOptions: function () {
            return {
                actions: false,
                height: this.widget_size_y - 90,
                width: this.widget_size_x - 40,
            };
        },
    });

    registry.add('altair', AltairWidget);
    return AltairWidget;
});
