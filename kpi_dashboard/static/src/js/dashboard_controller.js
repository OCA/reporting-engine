odoo.define('kpi_dashboard.DashboardController', function (require) {
    "use strict";

    var BasicController = require('web.BasicController');
    var core = require('web.core');
    var qweb = core.qweb;

    var _t = core._t;

    var DashboardController = BasicController.extend({
        custom_events: _.extend({}, BasicController.prototype.custom_events, {
            addDashboard: '_addDashboard',
        }),
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
    });

    return DashboardController;

});
