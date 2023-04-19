/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {_lt} from "@web/core/l10n/translation";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {Dialog} from "@web/core/dialog/dialog";

const {Component} = owl;

export class JoinNodeDialog extends Component {
    static components = {Dialog};
    static props = {
        close: Function,
        choices: {type: Array, element: Object},
        model_data: {type: Object},
        field_to_add: {type: Object},
        onJoinNodeChosen: Function,
    };
    setup() {
        super.setup();
        this._initChoices(this.props.choices, this.props.model_data);
    }
    _initChoices(choices, model_data) {
        for (var i = 0; i < choices.length; i++) {
            if (choices[i].join_node !== -1 && choices[i].table_alias !== -1) {
                choices[i].model_name = model_data[choices[i].table_alias].model_name;
            }
            choices[i].index = i;
        }
    }
    onChoiceClicked(event) {
        let elem = event.target;
        while (elem.localName !== "li") {
            elem = elem.parentNode;
        }
        this.props.onJoinNodeChosen(
            this.props.field_to_add,
            this.props.choices[elem.dataset.index]
        );
        this.props.close();
    }
}

JoinNodeDialog.template = "bi_view_editor.JoinNodeDialog";
