/** @odoo-module **/

/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

import {Component, onMounted, useRef, useState} from "@odoo/owl";

class FieldListItem extends Component {
    delete() {
        this.props.delete(this.props.field);
    }
    descriptionChanged(e) {
        this.props.setDescription(this.props.field, e.target.value);
    }
}
FieldListItem.template = "bi_view_editor.FieldListItem";
FieldListItem.props = {
    field: Object,
    delete: Function,
    setDescription: Function,
    readonly: Boolean,
};

class JoinListItem extends Component {}
JoinListItem.template = "bi_view_editor.JoinListItem";
JoinListItem.props = {
    field: Object,
    readonly: Boolean,
};

class FieldListContextMenu extends Component {
    setup() {
        this.main = useRef("main");
        onMounted(() => {
            $(this.main.el).css({
                left: this.props.position.x + "px",
                top: this.props.position.y + "px",
            });
        });
    }
    close() {
        this.props.close();
    }
    onChange(property, e) {
        this.props.onChange(this.props.field, property, e.target.checked);
    }
}
FieldListContextMenu.props = {
    field: Object,
    position: Object,
    close: Function,
    onChange: Function,
};

class FieldListFieldContextMenu extends FieldListContextMenu {
    get measurable() {
        const type = this.props.field.type;
        return type === "float" || type === "integer" || type === "monetary";
    }
}
FieldListFieldContextMenu.template = "bi_view_editor.FieldList.FieldContextMenu";

class FieldListJoinContextMenu extends FieldListContextMenu {}
FieldListJoinContextMenu.template = "bi_view_editor.FieldList.JoinContextMenu";

export class FieldList extends Component {
    setup() {
        this.state = useState({
            contextMenuOpen: null,
            contextMenuField: null,
            contextMenuPosition: null,
        });
    }
    setFieldProperty(field, property, value) {
        this.props.setFieldProperty(field, property, value);
        // This can trigger a recreation of all the field objects. If this is
        // called while the context menu is open, contextMenuField refers to a
        // field that is not in the list anymore. The reference must thus be
        // updated.
        if (this.state.contextMenuField !== null) {
            this.state.contextMenuField =
                this.props.fieldsByID[this.state.contextMenuField._id];
        }
    }
    setFieldDescription(field, description) {
        this.setFieldProperty(field, "description", description);
    }
    openContextMenu(which, field, e) {
        if (this.props.readonly) {
            return;
        }
        e.preventDefault();
        // Temporarily disable contextmenu for join node (until left join is implemented)
        if (field.join_node) {
            return;
        }
        this.state.contextMenuField = field;
        this.state.contextMenuPosition = {x: e.x - 20, y: e.y - 20};
        this.state.contextMenuOpen = which;
    }
    closeContextMenu() {
        this.state.contextMenuOpen = null;
        this.state.contextMenuField = null;
        this.state.contextMenuPosition = null;
    }
}
FieldList.template = "bi_view_editor.FieldList";
FieldList.components = {
    FieldListItem,
    JoinListItem,
    FieldListFieldContextMenu,
    FieldListJoinContextMenu,
};
FieldList.props = {
    fields: Object,
    fieldsByID: Object,
    deleteField: Function,
    setFieldProperty: Function,
    readonly: Boolean,
};
