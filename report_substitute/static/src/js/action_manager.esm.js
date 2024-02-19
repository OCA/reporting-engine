/** @odoo-module **/

import {registry} from "@web/core/registry";

registry
    .category("ir.actions.report handlers")
    .add("sustitution_handler", async function (action, options, env) {
        const orm = env.services.orm;
        const action_report_substitution_rule_ids = await orm.call(
            "ir.actions.report",
            "get_action_report_substitution_rule_ids",
            [action.id]
        );
        if (
            action.type === "ir.actions.report" &&
            action.context.active_ids &&
            action_report_substitution_rule_ids &&
            action_report_substitution_rule_ids.length !== 0
        ) {
            var active_ids = action.context.active_ids;
            const substitution = await orm.call(
                "ir.actions.report",
                "get_substitution_report_action",
                [action, active_ids]
            );
            Object.assign(action, substitution);
        }
        return Promise.resolve(false);
    });
