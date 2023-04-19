/** @odoo-module **/

import {registry} from "@web/core/registry";
import {_lt} from "@web/core/l10n/translation";
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {ModelFieldSelector} from "./model_field_selector";
import {FieldList} from "./field_list";
import {JoinNodeDialog} from "./join_node_dialog";

import {useService} from "@web/core/utils/hooks";

const {Component, useState, useEnv, reactive} = owl;

class Fields {
    constructor() {
        this.fields = [];
    }

    _initFieldValues(field) {
        field.row = typeof field.row === "undefined" ? false : field.row;
        field.column = typeof field.column === "undefined" ? false : field.column;
        field.measure = typeof field.measure === "undefined" ? false : field.measure;
        field.list = typeof field.list === "undefined" ? true : field.list;
        field._id = typeof field._id === "undefined" ? _.uniqueId("node_") : field._id;
        if (field.join_node) {
            field.join_left =
                typeof field.join_left === "undefined" ? false : field.join_left;
        }

        //var i = 0;
        //var name = field.name;
        //while (
        //    this.get().filter(function (item) {
        //        return item.name === field.name;
        //    }).length > 0
        //) {
        //    field.name = name + "_" + i;
        //    i++;
        //}
    }
    addField(field) {
        this._initFieldValues(field);
        this.fields.push(field);
    }
    removeField(field) {
        for (var i = 0; i < this.fields.length; i++) {
            if (this.fields[i].id === field.id) {
                this.fields.splice(i, 1);
                break;
            }
        }
    }
    updateField(field, option, value){
        for (var i = 0; i < this.fields.length; i++) {
            if (this.fields[i].id === field.id) {
                this.fields[i][option] = value;
                break;
            }
        }
    }
}

export class BiViewEditor extends Component {
    static components = {ModelFieldSelector, FieldList};
    static props = {...standardFieldProps};
    setup() {
        super.setup();
        this.fields = useState(new Fields());
        this.orm = useService("orm");
        this.dialogService = useService("dialog");
        this._initializeFields();
        this.addFieldAndJoinNode = this.addFieldAndJoinNode.bind(this);
    }
    removeField(event, field_to_remove) {
        this.fields.removeField(field_to_remove);
        this._updateValue();
    }
    updateOption(event, field) {
        let option = event.target.dataset.for;
        let value = event.target.checked;
        this.fields.updateField(field, option, value);
        this._updateValue();
    }
    addField(event, field_to_add) {
        let fields = this.fields.fields;
        this.orm.call("ir.model", "get_join_nodes", [fields, field_to_add]).then(
            function (result) {
                if (result.length === 1) {
                    this.addFieldAndJoinNode(field_to_add, result[0]);
                } else if (result.length > 1) {
                    this.dialogService.add(JoinNodeDialog, {
                        choices: result,
                        model_data: this.getModelData(),
                        field_to_add: field_to_add,
                        onJoinNodeChosen: this.addFieldAndJoinNode,
                    });
                } else {
                    field_to_add.table_alias = this.getTableAlias(field_to_add);
                    this.fields.addField(field_to_add);
                }
                this._updateValue();
            }.bind(this)
        );
    }
    addFieldAndJoinNode(field, join_node) {
        if (join_node.join_node === -1 || join_node.table_alias === -1) {
            field.table_alias = this.getTableAlias(field);
            if (join_node.join_node === -1) {
                join_node.join_node = field.table_alias;
            } else {
                join_node.table_alias = field.table_alias;
            }
            this.fields.addField(join_node);
        } else {
            field.table_alias = join_node.table_alias;
        }
        this.fields.addField(field);
    }
    getTableAlias(field) {
        if (typeof field.table_alias === "undefined") {
            var model_ids = this.getModelIds();
            var n = 1;
            while (typeof model_ids["t" + n] !== "undefined") {
                n++;
            }
            return "t" + n;
        } else {
            return field.table_alias;
        }
    }
    getModelIds() {
        let model_ids = {};
        this.fields.fields.forEach(
            (field) => (model_ids[field.table_alias] = field.model_id)
        );
        return model_ids;
    }
    getModelData() {
        let model_data = {};
        this.fields.fields.forEach(
            (field) =>
                (model_data[field.table_alias] = {
                    model_id: field.model_id,
                    model_name: field.model_name,
                })
        );
        return model_data;
    }
    _initializeFields() {
        this.fields.fields = JSON.parse(this.props.value);
    }
    _updateValue() {
        this.props.update(JSON.stringify(this.fields.fields));
    }
    clear() {
        // FIXME
        if (this.mode !== "readonly") {
            this.field_list.set([]);
        }
    }
    fieldListRemoved() {
        // FIXME
        var model = new Data.DataSet(this, "bve.view");
        model.call("get_clean_list", [this.lastSetValue]).then(
            function (result) {
                this.field_list.set(JSON.parse(result));
            }.bind(this)
        );
        this.loadAndPopulateModelList();
    }
}

BiViewEditor.template = "bi_view_editor.Frame";

registry.category("fields").add("bi_view_editor", BiViewEditor);
