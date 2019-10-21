// Copyright 2019 ACSONE SA/NV
// License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
odoo.define("report_substitute.action_report_substitute", function (require) {
    "use strict";

    var ActionManager = require("web.ActionManager");

    ActionManager.include({

        /**
         * Intercept action handling substitute the report action
         * @override
         */

        _handleAction: function (action, options) {
            if (action.type === "ir.actions.report" &&
                action.context.active_ids &&
                action.action_report_substitution_rule_ids &&
                action.action_report_substitution_rule_ids != 0) {
                var active_ids = action.context.active_ids;
                var self = this;
                var _super = this._super;
                var callersArguments = arguments;
                return this._rpc({
                    model: "ir.actions.report",
                    method: "get_substitution_report_action",
                    args: [action, active_ids]
                }).then(function (substitution_action) {
                    callersArguments[0] = substitution_action
                    return _super.apply(self, callersArguments);
                });

            }
            return this._super.apply(this, arguments);
        },

    });

});