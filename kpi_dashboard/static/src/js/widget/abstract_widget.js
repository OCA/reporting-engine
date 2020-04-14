odoo.define('kpi_dashboard.AbstractWidget', function (require) {
    "use strict";
    var Widget = require('web.Widget');
    var field_utils = require('web.field_utils');
    var time = require('web.time');
    var ajax = require('web.ajax');
    var registry = require('kpi_dashboard.widget_registry');

    var AbstractWidget = Widget.extend({
        template: 'kpi_dashboard.base_widget', // Template used by the widget
        cssLibs: [], // Specific css of the widget
        jsLibs: [], // Specific Javascript libraries of the widget
        events: {
            'click .o_kpi_dashboard_toggle_button': '_onClickToggleButton',
            'click .direct_action': '_onClickDirectAction',
        },
        init: function (parent, kpi_values) {
            this._super(parent);
            this.col = kpi_values.col;
            this.row = kpi_values.row;
            this.sizex = kpi_values.sizex;
            this.sizey = kpi_values.sizey;
            this.color = kpi_values.color;
            this.values = kpi_values;
            this.margin_x = parent.state.specialData.margin_x;
            this.margin_y = parent.state.specialData.margin_y;
            this.widget_dimension_x = parent.state.specialData.widget_dimension_x;
            this.widget_dimension_y = parent.state.specialData.widget_dimension_y;
            this.prefix = kpi_values.prefix;
            this.suffix = kpi_values.suffix;
            this.actions = kpi_values.actions;
            this.widget_size_x = this.widget_dimension_x * this.sizex +
                (this.sizex - 1) * this.margin_x;
            this.widget_size_y = this.widget_dimension_y * this.sizey +
                (this.sizey - 1) * this.margin_y;
        },
        willStart: function () {
            // We need to load the libraries before the start
            return $.when(ajax.loadLibs(this), this._super.apply(this, arguments));
        },
        start: function () {
            var self = this;
            return this._super.apply(this, arguments).then(function () {
                self._fillWidget(self.values);
            });
        },
        _onClickToggleButton: function (event) {
            event.preventDefault();
            this.$el.toggleClass('o_dropdown_open');
        },
        _fillWidget: function (values) {
            // This function fills the widget values
            if (this.$el === undefined)
                return;
            this.fillWidget(values);
            var item = this.$el.find('[data-bind="value_last_update_display"]');
            if (item && values.value_last_update !== undefined) {
                var value = field_utils.parse.datetime(values.value_last_update);
                item.text(value.clone().add(
                    this.getSession().getTZOffset(value), 'minutes').format(
                    time.getLangDatetimeFormat()
                ));
            }
            var $manage = this.$el.find('.o_kpi_dashboard_manage');
            if ($manage && this.showManagePanel(values))
                $manage.toggleClass('hidden', false);
        },
        showManagePanel: function (values) {
            // Hook for extensions
            return (values.actions !== undefined);
        },
        fillWidget: function (values) {
            // Specific function that will be changed by specific widget
            var value = values.value;
            var self = this;
            _.each(value, function (val, key) {
                var item = self.$el.find('[data-bind=' + key + ']')
                if (item)
                    item.text(val);
            })
        },
        _onClickDirectAction: function(event) {
            event.preventDefault();
            var $data = $(event.currentTarget).closest('a');
            return this.do_action($($data).data('id'));
        }
    });

    registry.add('abstract', AbstractWidget);
    return AbstractWidget;
});
