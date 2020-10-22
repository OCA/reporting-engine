odoo.define("kpi_dashboard.KpiFieldWidget", function (require) {
    "use strict";

    var basic_fields = require("web.basic_fields");
    var field_registry = require("web.field_registry");
    var core = require("web.core");
    var qweb = core.qweb;
    var registry = require("kpi_dashboard.widget_registry");

    var KpiFieldWidget = basic_fields.FieldChar.extend({
        jsLibs: ["/kpi_dashboard/static/lib/gridster/jquery.dsmorse-gridster.min.js"],
        cssLibs: ["/kpi_dashboard/static/lib/gridster/jquery.dsmorse-gridster.min.css"],
        className: "o_dashboard_view",
        _renderReadonly: function () {
            this.$el.html($(qweb.render("dashboard_kpi.dashboard")));
            var marginx = 0;
            var marginy = 0;
            var widgetx = 400;
            var widgety = 400;
            this.$el.find(".gridster").css("width", widgety);
            this.$grid = this.$el.find(".gridster ul");
            var widgetVals = {
                value: this.value,
                col: 1,
                row: 1,
                sizex: 1,
                sizey: 1,
                name: this.recordData[this.nodeOptions.name],
                value_last_update: this.recordData[this.nodeOptions.date],
            };
            var Widget = registry.getAny([
                this.recordData[this.nodeOptions.widget],
                "abstract",
            ]);
            this.state = {
                specialData: {
                    margin_x: marginx,
                    margin_y: marginy,
                    widget_dimension_x: widgetx,
                    widget_dimension_y: widgety,
                },
            };
            var widget = new Widget(this, widgetVals);
            var element = $(qweb.render("kpi_dashboard.kpi", {widget: widgetVals}));
            element.css("background-color", "white");
            element.css("color", "black");
            this.$grid.append(element);
            widget.appendTo(element);
            this.$grid
                .gridster({
                    widget_margins: [marginx, marginy],
                    widget_base_dimensions: [widgetx, widgety],
                    cols: 1,
                })
                .data("gridster")
                .disable();
        },
    });
    field_registry.add("kpi", KpiFieldWidget);
    return KpiFieldWidget;
});
