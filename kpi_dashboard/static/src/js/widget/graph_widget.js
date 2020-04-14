odoo.define('kpi_dashboard.GraphWidget', function (require) {
    "use strict";

    var AbstractWidget = require('kpi_dashboard.AbstractWidget');
    var registry = require('kpi_dashboard.widget_registry');
    var core = require('web.core');
    var qweb = core.qweb;


    var GraphWidget = AbstractWidget.extend({
        template: 'kpi_dashboard.graph',
        jsLibs: [
            '/web/static/lib/nvd3/d3.v3.js',
            '/web/static/lib/nvd3/nv.d3.js',
            '/web/static/src/js/libs/nvd3.js',
        ],
        cssLibs: [
            '/web/static/lib/nvd3/nv.d3.css',
        ],
        start: function () {
            this._onResize = this._onResize.bind(this);
            nv.utils.windowResize(this._onResize);
            return this._super.apply(this, arguments);
        },
        destroy: function () {
            if ('nv' in window && nv.utils && nv.utils.offWindowResize) {
                // if the widget is destroyed before the lazy loaded libs (nv) are
                // actually loaded (i.e. after the widget has actually started),
                // nv is undefined, but the handler isn't bound yet anyway
                nv.utils.offWindowResize(this._onResize);
            }
            this._super.apply(this, arguments);
        },
        _getChartOptions: function (values) {
            return {
                x: function (d, u) { return u; },
                margin: {'left': 0, 'right': 0, 'top': 5, 'bottom': 0},
                showYAxis: false,
                showXAxis: false,
                showLegend: false,
                height: this.widget_size_y - 90,
                width: this.widget_size_x - 20,
            };
        },
        _chartConfiguration: function (values) {

            this.chart.forceY([0]);
            this.chart.xAxis.tickFormat(function (d) {
                var label = '';
                _.each(values.value.graphs, function (v) {
                    if (v.values[d] && v.values[d].x) {
                        label = v.values[d].x;
                    }
                });
                return label;
            });
            this.chart.yAxis.tickFormat(d3.format(',.2f'));

            this.chart.tooltip.contentGenerator(function (key) {
                return qweb.render('GraphCustomTooltip', {
                    'color': key.point.color,
                    'key': key.series[0].title,
                    'value': d3.format(',.2f')(key.point.y)
                });
            });
        },
        _addGraph: function (values) {
            var data = values.value.graphs;
            this.$svg.addClass('o_graph_linechart');
            this.chart = nv.models.lineChart();
            this.chart.options(
                this._getChartOptions(values)
            );
            this._chartConfiguration(values);
            d3.select(this.$('svg')[0])
                .datum(data)
                .transition().duration(600)
                .call(this.chart);
            this.$('svg').css('height', this.widget_size_y - 90);
            this._customizeChart();
        },
        fillWidget: function (values) {
            var self = this;
            var element = this.$el.find('[data-bind="value"]');
            element.empty();
            element.css('padding-left', 10).css('padding-right', 10);
            this.chart = null;
            nv.addGraph(function () {
                self.$svg = self.$el.find(
                    '[data-bind="value"]'
                ).append('<svg width=' + (self.widget_size_x - 20) + '>');
                self._addGraph(values);
            });
        },
        _customizeChart: function () {
            // Hook function
        },
        _onResize: function () {
            if (this.chart) {
                this.chart.update();
                this._customizeChart();
            }
        },
    });

    registry.add('graph', GraphWidget);
    return GraphWidget;
});
