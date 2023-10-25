/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, onWillUpdateProps, useState} from "@odoo/owl";
import {FIELD_DATA_TYPE, ModelList} from "./model_list.esm";
import {FieldList} from "./field_list.esm";
import {JoinNodeDialog} from "./join_node_dialog.esm";
import {registry} from "@web/core/registry";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {useService} from "@web/core/utils/hooks";

export class BiViewEditor extends Component {
    setup() {
        this.state = useState({
            models: [],
            fields: [],
            // This allows to access fields by their _id property in an
            // efficient way. Since the fields array length is normally quite
            // small, it would also be possible to use
            // fields.find(element => element._id == field._id), but that
            // would mean that this function would be defined in 3 places
            // (deleteField(), setFieldProperty() and
            // FieldList.setFieldProperty()), and using a common function
            // would be quite similar to using this object.
            fieldsByID: {},
        });
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        onWillUpdateProps((nextProps) => {
            this.updateFields(nextProps.value);
        });
        this.updateFields(this.props.value);
    }
    get modelIDs() {
        const model_ids = {};
        for (const field of this.state.fields) {
            model_ids[field.table_alias] = field.model_id;
        }
        return model_ids;
    }
    get modelData() {
        const model_data = {};
        for (const field of this.state.fields) {
            model_data[field.table_alias] = {
                model_id: field.model_id,
                model_name: field.model_name,
            };
        }
        return model_data;
    }
    _addField(field) {
        field.row = typeof field.row === "undefined" ? false : field.row;
        field.column = typeof field.column === "undefined" ? false : field.column;
        field.measure = typeof field.measure === "undefined" ? false : field.measure;
        field.list = typeof field.list === "undefined" ? true : field.list;
        field._id = typeof field._id === "undefined" ? _.uniqueId("node_") : field._id;
        if (field.join_node) {
            field.join_left =
                typeof field.join_left === "undefined" ? false : field.join_left;
        }

        let i = 0;
        const name = field.name;
        while (
            this.state.fields.filter(function (item) {
                return item.name === field.name;
            }).length > 0
        ) {
            field.name = name + "_" + i;
            i++;
        }
        this.state.fields.push(field);
        this.state.fieldsByID[field._id] = field;
    }
    deleteField(field) {
        this.state.fields.splice(
            this.state.fields.findIndex((element) => {
                return element._id === field._id;
            }),
            1
        );
        delete this.state.fieldsByID[field._id];
        this.fieldDeleted();
    }
    setFieldProperty(field, property, value) {
        this.state.fieldsByID[field._id][property] = value;
        this.fieldUpdated();
    }
    setFields(fields) {
        this.state.fields = [];
        this.state.fieldsByID = {};
        for (const field of fields) {
            this._addField(field);
        }
    }
    updateFields(value) {
        if (value) {
            this.setFields(JSON.parse(value));
        }
        this.updateModels();
    }
    updateModels() {
        const model_ids = this.modelIDs;
        this.orm
            .call("ir.model", "get_models", model_ids ? [model_ids] : [])
            .then((models) => {
                this.state.models = models;
            });
    }
    clear() {
        if (this.props.readonly) {
            return;
        }
        this.setFields([]);
        this.updateValue();
    }
    fieldUpdated() {
        this.updateValue();
    }
    fieldDeleted() {
        this.orm
            .call("bve.view", "get_clean_list", [this.state.fields])
            .then((result) => {
                this.updateFields(result);
                this.updateValue();
            });
    }
    getTableAlias(field) {
        if (typeof field.table_alias === "undefined") {
            const model_ids = this.modelIDs;
            let n = 1;
            while (typeof model_ids["t" + n] !== "undefined") {
                n++;
            }
            return "t" + n;
        }
        return field.table_alias;
    }
    addFieldAndJoinNode(field, join_node) {
        if (join_node.join_node === -1 || join_node.table_alias === -1) {
            field.table_alias = this.getTableAlias(field);
            if (join_node.join_node === -1) {
                join_node.join_node = field.table_alias;
            } else {
                join_node.table_alias = field.table_alias;
            }
            this._addField(join_node);
        } else {
            field.table_alias = join_node.table_alias;
        }

        this._addField(field);
        this.updateValue();
    }
    addField(field) {
        const data = _.extend({}, field);
        const field_data = this.state.fields;
        this.orm
            .call("ir.model", "get_join_nodes", [field_data, data])
            .then((result) => {
                if (result.length === 1) {
                    this.addFieldAndJoinNode(data, result[0]);
                } else if (result.length > 1) {
                    this.dialogService.add(JoinNodeDialog, {
                        choices: result,
                        model_data: this.modelData,
                        choiceSelected: (choice) => {
                            this.addFieldAndJoinNode(data, choice);
                        },
                    });
                } else {
                    data.table_alias = this.getTableAlias(data);
                    this._addField(data);
                    this.updateValue();
                }
            });
    }
    fieldClicked(field) {
        this.addField(field);
    }
    onDragOver(e) {
        if (this.props.readonly) {
            return;
        }
        const dragType = e.dataTransfer.types[0];
        if (dragType === FIELD_DATA_TYPE) {
            e.preventDefault();
            e.dataTransfer.dropEffect = "copy";
        }
    }
    onDrop(e) {
        if (this.props.readonly) {
            return;
        }
        const dragData = e.dataTransfer.getData(FIELD_DATA_TYPE);
        if (dragData) {
            e.preventDefault();
            this.addField(JSON.parse(dragData));
        }
    }
    updateValue() {
        this.props.update(JSON.stringify(this.state.fields));
        this.updateModels();
    }
}
BiViewEditor.template = "bi_view_editor.Frame";
BiViewEditor.components = {
    ModelList,
    FieldList,
};
BiViewEditor.props = {
    ...standardFieldProps,
};

registry.category("fields").add("BVEEditor", BiViewEditor);
