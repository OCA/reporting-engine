/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {registry} from "@web/core/registry";
import {_lt} from "@web/core/l10n/translation";
import {standardFieldProps} from "@web/views/fields/standard_field_props";

import {Widget} from "@web/views/widgets/widget";
const {Component, useState} = owl;

export class FieldContextMenu extends Component {
    static props = {
        field: {type: Object},
        updateOption: Function,
    };
    setup(){
        super.setup();
        this.measureable = useState({"value":
            this.props.field.type === "float" ||
            this.props.field.type === "integer" ||
            this.props.field.type === "monetary"});
    }
}

export class FieldListFieldContextMenu extends Component {
    open(x, y, $item) {

        var measureable =
            field.type === "float" ||
            field.type === "integer" ||
            field.type === "monetary";
        this.$el.find(".checkbox-column").attr("disabled", measureable);
        this.$el.find(".checkbox-row").attr("disabled", measureable);
        this.$el.find(".checkbox-measure").attr("disabled", !measureable);
        this.$el.find(".checkbox-list").attr("disabled", false);
    }
}

//export class FieldListJoinContextMenu extends Component {
//    open(x, y, $item) {
//        var node = $item.data("field");
//        this.$el.find(".checkbox-join-left").prop("checked", node.join_left);
//
//        var events = this._super(x, y, node);
//        this.$el.find("input").unbind("change");
//        this.$el.find("input").change(function () {
//            var $checkbox = $(this);
//            var property = $checkbox.attr("data-for");
//            node[property] = $checkbox.is(":checked");
//            events.trigger("change", node);
//        });
//        return events;
//    }
//}

export class FieldListItem extends Component {
    static components = {FieldContextMenu};
    static props = {
        field: {type: Object},
        onFieldRemove: Function,
        updateOption: Function,
    };
    setup(){
        //super.setup();
        this.contextMenu = useState({"value": false});
    }
    showContextMenu(event){
        console.log
        this.contextMenu.value = true;
    }
    hideContextMenu(event){
        this.contextMenu.value = false;
    }
}

export class FieldList extends Component {
    static props = {
        onFieldRemove: Function,
        updateOption: Function,
        fields: {type: Array, elem: Object},
    };
    static components = {FieldListItem};
    //events: {
    //    'keyup input[name="description"]': "keyupDescription",
    //};
}

FieldList.template = "bi_view_editor.FieldList";
FieldListItem.template = "bi_view_editor.FieldListItem";
FieldContextMenu.template = "bi_view_editor.FieldContextMenu";
FieldListFieldContextMenu.template = "bi_view_editor.FieldListFieldContextMenu";
//FieldListJoinContextMenu.template = "bi_view_editor.FieldListJoinContextMenu";
