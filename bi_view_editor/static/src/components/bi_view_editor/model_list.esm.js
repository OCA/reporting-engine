/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, useState} from "@odoo/owl";
import {useService} from "@web/core/utils/hooks";

export const FIELD_DATA_TYPE = "application/x-odoo-bve-field";

class ModelListFieldItem extends Component {
    clicked() {
        if (this.props.readonly) {
            return;
        }
        this.props.fieldClicked(this.props.field);
    }
    onDragStart(e) {
        if (this.props.readonly) {
            return;
        }
        e.dataTransfer.setData(FIELD_DATA_TYPE, JSON.stringify(this.props.field));
    }
}
ModelListFieldItem.template = "bi_view_editor.ModelListFieldItem";
ModelListFieldItem.props = {
    field: Object,
    fieldClicked: Function,
    readonly: Boolean,
};

class ModelListItem extends Component {
    setup() {
        this.state = useState({
            expanded: false,
            fields: [],
        });
        this._loaded = false;
        this.orm = useService("orm");
    }
    _loadFields() {
        if (this._loaded) {
            return;
        }
        this._loaded = true;
        this.orm
            .call("ir.model", "get_fields", [this.props.model.id])
            .then((fields) => {
                this.state.fields = fields;
            });
    }
    clicked() {
        if (this.props.readonly) {
            return;
        }
        this.expanded = !this.expanded;
    }
    get matchesFilter() {
        const filter = this.props.filter;
        if (!filter) {
            return true;
        }
        const model = this.props.model;
        const result =
            model.name.toLowerCase().indexOf(filter) !== -1 ||
            model.model.toLowerCase().indexOf(filter) !== -1;
        if (!result) {
            // Filtered-out items should be collapsed
            this.expanded = false;
        }
        return result;
    }
    get expanded() {
        return this.state.expanded && !this.props.readonly;
    }
    set expanded(expanded) {
        if (expanded === this.state.expanded) {
            return;
        }
        if (expanded) {
            this._loadFields();
        }
        this.state.expanded = expanded;
    }
}
ModelListItem.template = "bi_view_editor.ModelListItem";
ModelListItem.components = {
    ModelListFieldItem,
};
ModelListItem.props = {
    model: Object,
    filter: String,
    fieldClicked: Function,
    readonly: Boolean,
};

export class ModelList extends Component {
    setup() {
        this.state = useState({
            filter: "",
        });
    }
    filterChanged(e) {
        this.state.filter = e.target.value;
    }
}
ModelList.template = "bi_view_editor.ModelList";
ModelList.components = {
    ModelListItem,
};
ModelList.props = {
    models: Object,
    fieldClicked: Function,
    readonly: Boolean,
};
