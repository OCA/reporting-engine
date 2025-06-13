import {registry} from "@web/core/registry";

registry
    .category("ir.actions.report handlers")
    .add("substitution_handler", async function (action, options, env) {
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

            // Prevent infinite loops if no substitution is found
            if (substitution.id === action.id) {
                return;
            }

            const handlers = registry.category("ir.actions.report handlers").getAll();
            for (const handler of handlers) {
                const result = await handler(substitution, options, env);
                if (result) {
                    return result;
                }
            }
        }
        return Promise.resolve(false);
    });
