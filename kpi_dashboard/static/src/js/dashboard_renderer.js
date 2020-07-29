odoo.define('kpi_dashboard.DashboardRenderer', function (require) {
    "use strict";

    var BasicRenderer = require('web.BasicRenderer');
    var core = require('web.core');
    var registry = require('kpi_dashboard.widget_registry');
    var BusService = require('bus.BusService');
    var qweb = core.qweb;

    var DashboardRenderer= BasicRenderer.extend({
        className: "o_dashboard_view",
        _getDashboardWidget: function (kpi) {
            var Widget = registry.getAny([
                kpi.widget, 'abstract',
            ]);
            var widget = new Widget(this, kpi);
            return widget;
        },
        _onClickModifyContext: function (modify_context_expression, event) {
            this.trigger_up('modify_context', {
                context: modify_context_expression,
                event: event,
            })
        },
        _renderView: function () {
            this.$el.html($(qweb.render('dashboard_kpi.dashboard')));
            this.$el.css(
                'background-color', this.state.specialData.background_color);
            this.$el.find('.gridster')
                .css('width', this.state.specialData.width);
            this.$grid = this.$el.find('.gridster ul');
            var self = this;
            this.kpi_widget = {};
            _.each(this.state.specialData.item_ids, function (kpi) {
                var element = $(qweb.render(
                    'kpi_dashboard.kpi', {widget: kpi}));
                element.css('background-color', kpi.color);
                element.css('color', kpi.font_color);
                element.attr('id', _.uniqueId('kpi_'));
                self.$grid.append(element);
                if (kpi.modify_color) {
                    self.trigger_up("add_modify_color", {
                        element_id: element.attr("id"),
                        expression: kpi.modify_color_expression,
                    })
                }
                if (kpi.modify_context) {
                    element.on("click", self._onClickModifyContext.bind(
                        self, kpi.modify_context_expression));
                    element.css('cursor', 'pointer');
                    // We want to set it show as clickable
                }
                self.kpi_widget[kpi.id] = self._getDashboardWidget(kpi);
                self.kpi_widget[kpi.id].appendTo(element);
            });
            this.$grid.gridster({
                widget_margins: [
                    this.state.specialData.margin_x,
                    this.state.specialData.margin_y,
                ],
                widget_base_dimensions: [
                    this.state.specialData.widget_dimension_x,
                    this.state.specialData.widget_dimension_y,
                ],
                cols: this.state.specialData.max_cols,
            }).data('gridster').disable();
            this.channel = 'kpi_dashboard_' + this.state.res_id;
            this.call(
                'bus_service', 'addChannel', this.channel);
            this.call('bus_service', 'startPolling');
            this.call(
                'bus_service', 'onNotification',
                this, this._onNotification
            );
            if (this.state.specialData.compute_on_fly_refresh > 0) {
                // Setting the refresh interval
                this.on_fly_interval = setInterval(function () {
                    self.trigger_up('refresh_on_fly');
                }, this.state.specialData.compute_on_fly_refresh *1000);
            };
            this.trigger_up('refresh_colors');
            this.trigger_up('refresh_on_fly');
            // We need to refreshs data in order compute with the current
            // context
            return $.when();
        },
        on_detach_callback: function () {
            // We want to clear the refresh interval once we exit the view
            if (this.on_fly_interval) {
                clearInterval(this.on_fly_interval)
            }
            this._super.apply(this, arguments);
        },
        _onNotification: function (notifications) {
            var self = this;
            _.each(notifications, function (notification) {
                var channel = notification[0];
                var message = notification[1];
                if (channel === self.channel && message) {
                    var widget = self.kpi_widget[message.id];
                    if (widget !== undefined) {
                        widget._fillWidget(message);
                    }
                }
            });
        },
    });

    return DashboardRenderer;
});
