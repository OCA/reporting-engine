/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {_lt} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

const {Component, useState, useEnv} = owl;

export class ModelListFieldItem extends Component {
    static props = {
        field: {type: Object},
        onFieldClicked: Function,
    };
}

export class ModelListItem extends Component {
    static components = {ModelListFieldItem};
    static props = {
        model: {type: Object},
        onFieldClicked: Function,
    };
    setup() {
        super.setup();
        this.fields = useState([]);
        this.active = useState({value: false});
        this.orm = useService("orm");
    }
    async modelClicked(event) {
        await this.loadFields();
        this.active.value = !this.active.value;
    }
    async loadFields() {
        const model_id = this.props.model.id;
        if (this.fields.length === 0) {
            this.fields = await this.orm.call("ir.model", "get_fields", [model_id]);
        }
    }
    get displayedFields() {
        if (this.active.value === true) {
            return this.fields;
        } else {
            return [];
        }
    }
}

export class ModelFieldSelector extends Component {
    static components = {ModelListItem};
    static props = {
        onFieldClicked: Function,
    };
    setup() {
        super.setup();
        this.orm = useService("orm");
        this.models = useState([]);
        this.cache_fields = {};
        this.filter = useState({value: ""});
        this.mode = null;
        this.loadModels([]);
    }
    get displayedModels() {
        const models = this.models;
        const filter = this.filter.value;
        if (filter === "") {
            return models;
        } else {
            return models.filter(
                (m) =>
                    m.name.toLowerCase().indexOf(filter) !== -1 &&
                    m.model.toLowerCase().indexOf(filter) !== -1
            );
        }
    }
    async loadModels(model_ids) {
        this.models = await this.orm.call(
            "ir.model",
            "get_models",
            model_ids ? [model_ids] : []
        );
    }
    filterChanged(event) {
        this.filter.value = event.target.value.toLowerCase();
    }
}

ModelFieldSelector.template = "bi_view_editor.ModelFieldSelector";
ModelListItem.template = "bi_view_editor.ModelListItem";
ModelListFieldItem.template = "bi_view_editor.ModelListFieldItem";
