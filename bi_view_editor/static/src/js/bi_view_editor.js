/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('bi_view_editor', function (require) {
    "use strict";

    var JoinNodeDialog = require('bi_view_editor.JoinNodeDialog');
    var ModelList = require('bi_view_editor.ModelList');
    var FieldList = require('bi_view_editor.FieldList').FieldList;

    var AbstractField = require('web.AbstractField');
    var Data = require('web.data');
    var field_registry = require('web.field_registry');

    var BiViewEditor = AbstractField.extend({
        template: "bi_view_editor.Frame",
        events: {
            "click .clear-btn": "clear",
        },
        start: function () {
            var self = this;
            var res = this._super.apply(this, arguments);

            // Init ModelList
            this.model_list = new ModelList(this);
            this.model_list.appendTo(this.$(".body > .left"));
            this.model_list.on('field_clicked', this, function (field) {
                self.addField(_.extend({}, field));
            });

            // Init FieldList
            this.field_list = new FieldList(this);
            this.field_list.appendTo(this.$(".body > .right"));
            this.field_list.on('removed', this, this.fieldListRemoved);
            this.field_list.on('updated', this, this.fieldListChanged);

            this.$el.find(".body > .right").droppable({
                accept: "div.class-list div.field",
                drop: function (event, ui) {
                    self.addField(_.extend({}, ui.draggable.data('field')));
                    ui.draggable.draggable('option', 'revert', false);
                },
            });

            this.on("change:effective_readonly", this, function () {
                this.updateMode();
            });
            this.renderValue();
            this.loadAndPopulateModelList();
            this.updateMode();
            return res;
        },
        clear: function () {
            if (this.mode !== 'readonly') {
                this.field_list.set([]);
                this.loadAndPopulateModelList();
                this._setValue(this.field_list.get());
            }
        },
        fieldListChanged: function () {
            this._setValue(this.field_list.get());
        },
        fieldListRemoved: function () {
            console.log(this.field_list.get());
            this._setValue(this.field_list.get());
            var model = new Data.DataSet(this, "bve.view");
            model.call('get_clean_list', [this.value]).then(function (result) {
                this.field_list.set(JSON.parse(result));
                this._setValue(this.field_list.get());
            }.bind(this));
            this.loadAndPopulateModelList();
        },
        renderValue: function () {
            this.field_list.set(JSON.parse(this.value));
        },
        updateMode: function () {
            if (this.mode === 'readonly') {
                this.$el.find('.clear-btn').addClass('d-none');
                this.$el.find(".body .right").droppable("option", "disabled", true);
            } else {
                this.$el.find('.clear-btn').removeClass('d-none');
                this.$el.find('.body .right').droppable('option', 'disabled', false);
            }
            this.field_list.setMode(this.mode);
            this.model_list.setMode(this.mode);
        },
        loadAndPopulateModelList: function () {
            var model_ids = null;
            if (this.field_list.get().length > 0) {
                model_ids = this.field_list.getModelIds();
            }
            this.model_list.loadModels(model_ids).done(function (models) {
                this.model_list.populateModels(models);
            }.bind(this));
        },
        getTableAlias: function (field) {
            if (typeof field.table_alias === 'undefined') {
                var model_ids = this.field_list.getModelIds();
                var n = 1;
                while (typeof model_ids["t" + n] !== 'undefined') {
                    n++;
                }
                return "t" + n;
            }
            return field.table_alias;
        },
        addFieldAndJoinNode: function (field, join_node) {
            if (join_node.join_node === -1 || join_node.table_alias === -1) {
                field.table_alias = this.getTableAlias(field);
                if (join_node.join_node === -1) {
                    join_node.join_node = field.table_alias;
                } else {
                    join_node.table_alias = field.table_alias;
                }
                this.field_list.add(join_node);
            } else {
                field.table_alias = join_node.table_alias;
            }

            this.field_list.add(field);
            this.loadAndPopulateModelList();
            this._setValue(this.field_list.get());
        },
        addField: function (field) {
            var data = _.extend({}, field);
            var model = new Data.DataSet(this, "ir.model");
            var field_data = this.field_list.get();
            model.call('get_join_nodes', [field_data, data]).then(function (result) {
                if (result.length === 1) {
                    this.addFieldAndJoinNode(data, result[0]);
                } else if (result.length > 1) {
                    var dialog = new JoinNodeDialog(this, {}, result, this.field_list.getModelData());
                    dialog.open().on('chosen', this, function (e) {
                        this.addFieldAndJoinNode(data, e.choice);
                    });
                } else {
                    data.table_alias = this.getTableAlias(data);
                    this.field_list.add(data);
                    this.loadAndPopulateModelList();
                    this._setValue(this.field_list.get());
                }
            }.bind(this));
        },
        _parseValue: function (value) {
            return JSON.stringify(value);
        },
    });

    field_registry.add('BVEEditor', BiViewEditor);

});
