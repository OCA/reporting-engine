odoo.define('kpi_dashboard.DashboardController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var core = require('web.core');
    var qweb = core.qweb;

    var _t = core._t;

    var DashboardController = BasicController.extend({
        init: function () {
            this._super.apply(this, arguments);
            this.dashboard_context = {};
            this.dashboard_color_data = []
        },
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            addDashboard: '_addDashboard',
            refresh_on_fly: '_refreshOnFly',
            modify_context: '_modifyContext',
            add_modify_color: '_addModifyColor',
            refresh_colors: '_refreshColors',
        }),
        _refreshOnFly: function (event) {
            var self = this;
            this._rpc({
                model: this.modelName,
                method: 'read_dashboard_on_fly',
                args: [[this.renderer.state.res_id]],
                context: this._getContext(),
            }).then(function (data) {
                _.each(data, function (item) {
                    // We will follow the same logic used on Bus Notifications
                    self.renderer._onNotification([[
                        "kpi_dashboard_" + self.renderer.state.res_id,
                        item
                    ]])
                });
            });
        },
        renderPager: function ($node, options) {
            options = _.extend({}, options, {
                validate: this.canBeDiscarded.bind(this),
            });
            this._super($node, options);
        },
        _pushState: function (state) {
            state = state || {};
            var env = this.model.get(this.handle, {env: true});
            state.id = env.currentId;
            this._super(state);
        },
        _addDashboard: function () {
            var self = this;
            var action = self.initialState.specialData.action_id;
            var name = self.initialState.specialData.name;
            if (! action) {
                self.do_warn(_t("First you must create the Menu"));
            }
            return self._rpc({
                route: '/board/add_to_dashboard',
                params: {
                    action_id: action,
                    context_to_save: {'res_id': self.initialState.res_id},
                    domain: [('id', '=', self.initialState.res_id)],
                    view_mode: 'dashboard',
                    name: name,
                },
            })
            .then(function (r) {
                if (r) {
                    self.do_notify(
                        _.str.sprintf(_t("'%s' added to dashboard"), name),
                        _t('Please refresh your browser for the changes to take effect.')
                    );
                } else {
                    self.do_warn(_t("Could not add KPI dashboard to dashboard"));
                }
            });
        },
        _updateButtons: function () {
            // HOOK Function
            this.$buttons.on(
                'click', '.o_dashboard_button_add',
                this._addDashboard.bind(this));
        },
        renderButtons: function ($node) {
            if (! $node) {
                return;
            }

            this.$buttons = $('<div/>');
            this.$buttons.append(qweb.render(
                "kpi_dashboard.buttons", {widget: this}));

            this._updateButtons();
            this.$buttons.appendTo($node);
        },
        _getContext: function () {
            return _.extend(
                {},
                this.model.get(this.handle, {raw: true}).getContext(),
                {bin_size: true},
                this.dashboard_context,
            )
        },
        _modifyContext: function (event) {
            var ctx = this._getContext();
            this.dashboard_context = _.extend(
                this.dashboard_context,
                py.eval(event.data.context, {context: _.extend(
                    ctx,
                    {__getattr__: function() {return false}}
                    // We need to add this in order to allow to use undefined
                    // context items
                )}),
            );
            this._refreshOnFly(event);
            this._refreshColors();
        },
        _addModifyColor: function (event) {
            this.dashboard_color_data.push([
                event.data.element_id,
                event.data.expression,
            ]);
        },
        _refreshColors: function () {
            var self = this;
            var ctx = this._getContext();
            _.each(this.dashboard_color_data, function (data) {
                var color = py.eval(data[1], {
                    context: _.extend(ctx, {
                        __getattr__: function() {return false},

                    }),
                    check_if: function(args) {
                        if (args[0].toJSON()) {
                            return args[1];
                        }
                        return args[2];
                    }
                });
                var $element = self.renderer.$el.find('#' + data[0]);
                $element.css('background-color', color);
            });
        },
    });

    return DashboardController;

});
