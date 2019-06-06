/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('bi_view_editor.ModelList', function (require) {
    "use strict";

    var Widget = require('web.Widget');
    var core = require('web.core');
    var qweb = core.qweb;

    var ModelList = Widget.extend({
        template: 'bi_view_editor.ModelList',
        events: {
            'keyup .search-bar > input': 'filterChanged',
        },
        init: function (parent) {
            var res = this._super(parent);
            this.active_models = [];
            this.cache_fields = {};
            this.current_filter = '';
            this.mode = null;
            return res;
        },
        setMode: function (mode) {
            if (mode === 'readonly') {
                this.$el.find('.search-bar').attr('disabled', true);
                this.$el.find('.class-list, .class').addClass('readonly');
            } else {
                this.$el.find('.search-bar').attr('disabled', false);
                this.$el.find('.class-list, .class').removeClass('readonly');
            }
            this.mode = mode;
        },
        isActive: function (id) {
            return this.active_models.indexOf(id) !== -1;
        },
        removeAsActive: function (id) {
            var i = this.active_models.indexOf(id);
            this.active_models.splice(i, 1);
        },
        addAsActive: function (id) {
            this.active_models.push(id);
        },
        loadModels: function (model_ids) {
            return this._rpc({
                model: 'ir.model',
                method: 'get_models',
                args: model_ids ? [model_ids] : [],
            });
        },
        loadFields: function (model_id) {
            if (!(model_id in this.cache_fields)) {
                var deferred = this._rpc({
                    model: 'ir.model',
                    method: 'get_fields',
                    args: [model_id],
                });
                this.cache_fields[model_id] = deferred;
            }
            return this.cache_fields[model_id];
        },
        populateModels: function (models) {
            var self = this;
            this.$el.find(".class-list").html('');

            _.each(models, function (model) {
                var $html = $(qweb.render('bi_view_editor.ModelListItem', {
                    'id': model.id,
                    'model': model.model,
                    'name': model.name,
                }));
                $html.find('.class').data('model', model).click(function () {
                    self.modelClicked($(this));
                });
                self.$el.find(".class-list").append($html);

                if (self.isActive(model.id)) {
                    self.loadFields(model.id).done(function (fields) {
                        self.populateFields(fields, model.id);
                    });
                }
            });
        },
        populateFields: function (fields, model_id) {
            var self = this;
            if (!model_id && fields.length === 0) {
                return;
            }
            var data_model_id = model_id;
            if (!data_model_id) {
                data_model_id = fields[0].model_id;
            }
            var $model_item = this.$el.find(".class[data-id='" + data_model_id + "']");
            _.each(fields, function (field) {
                var $field = $(qweb.render('bi_view_editor.ModelListFieldItem', {
                    name: field.name,
                    description: field.description,
                })).data('field', field).click(function () {
                    self.fieldClicked($(this));
                }).draggable({
                    'revert': 'invalid',
                    'scroll': false,
                    'helper': 'clone',
                    'appendTo': 'body',
                    'containment': 'window',
                });
                $model_item.after($field);

            });
        },
        modelClicked: function ($el) {
            if (this.mode === 'readonly') {
                return;
            }
            var model = $el.data('model');
            $el.parent().find('.field').remove();
            if (this.isActive(model.id)) {
                this.removeAsActive(model.id);
            } else {
                this.addAsActive(model.id);
                this.loadFields(model.id).done(function (fields) {
                    this.populateFields(fields, model.id);
                }.bind(this));
            }
        },
        fieldClicked: function ($el) {
            if (this.mode === 'readonly') {
                return;
            }
            this.trigger('field_clicked', $el.data('field'));
        },
        filterChanged: function (e) {
            var $input = $(e.target);
            this.filter($input.val());
        },
        filter: function (value) {
            this.active_models = [];
            this.$el.find('.field').remove();
            var val = typeof value === 'undefined' ? this.current_filter : value.toLowerCase();
            this.$el.find(".class").each(function () {
                var data = $(this).data('model');
                if (data.name.toLowerCase().indexOf(val) === -1 &&
                    data.model.toLowerCase().indexOf(val) === -1) {
                    $(this).addClass('d-none');
                } else {
                    $(this).removeClass('d-none');
                }
            });
            this.current_filter = val;
        },
    });

    return ModelList;

});
