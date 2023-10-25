/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component} from "@odoo/owl";
import {Dialog} from "@web/core/dialog/dialog";

export class JoinNodeDialog extends Component {
    setup() {
        this.title = this.env._t("Join...");
        this.choices = [];
        const model_data = this.props.model_data;
        // Prepare data for view
        for (let i = 0; i < this.props.choices.length; i++) {
            // Props must not be modified
            const choice = _.extend({}, this.props.choices[i]);
            if (choice.join_node !== -1 && choice.table_alias !== -1) {
                choice.model_name = model_data[choice.table_alias].model_name;
            }
            choice.index = i;
            this.choices.push(choice);
        }
    }
    choiceClicked(choice) {
        this.props.close();
        this.props.choiceSelected(choice);
    }
}
JoinNodeDialog.template = "bi_view_editor.JoinNodeDialog";
JoinNodeDialog.props = {
    close: Function,
    choices: Object,
    model_data: Object,
    choiceSelected: Function,
};
JoinNodeDialog.components = {
    Dialog,
};
