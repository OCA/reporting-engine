/* Copyright 2015-2018 Onestein (<http://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('bi_view_editor.FieldList', function (require) {
    "use strict";

    var core = require('web.core');
    var qweb = core.qweb;
    var Widget = require('web.Widget');

    var FieldListContextMenu = Widget.extend({
        start: function () {
            var res = this._super.apply(this, arguments);
            this.$el.mouseleave(function () {
                $(this).addClass('hidden');
            });
            return res;
        },
        open: function (x, y) {
            this.$el.css({
                'left': x + 'px',
                'top': y + 'px'
            });
            this.$el.removeClass('hidden');
            return _.extend({}, window.Backbone.Events);
        }
    });

    var FieldListFieldContextMenu = FieldListContextMenu.extend({
        template: 'bi_view_editor.FieldList.FieldContextMenu',
        open: function (x, y, field) {
            this.$el.find('.checkbox-column').prop('checked', field.column);
            this.$el.find('.checkbox-row').prop('checked', field.row);
            this.$el.find('.checkbox-measure').prop('checked', field.measure);
            this.$el.find('.checkbox-list').prop('checked', field.list);

            var measureable =
                field.type === "float" ||
                field.type === "integer" ||
                field.type === "monetary"
            ;

            this.$el.find('.checkbox-column').attr('disabled', measureable);
            this.$el.find('.checkbox-row').attr('disabled', measureable);
            this.$el.find('.checkbox-measure').attr('disabled', !measureable);
            this.$el.find('.checkbox-list').attr('disabled', false);

            var events = this._super(x, y, field);
            this.$el.find('input').unbind('change');
            this.$el.find('input').change(function () {
                var $checkbox = $(this);
                var property = $checkbox.attr('data-for');
                field[property] = $checkbox.is(':checked');
                events.trigger('change', field);
            });

            return events;
        }
    });

    var FieldListJoinContextMenu = FieldListContextMenu.extend({
        template: 'bi_view_editor.FieldList.JoinContextMenu',
        open: function (x, y, node) {
            this.$el.find('.checkbox-join-left').prop('checked', node.join_left);

            var events = this._super(x, y, node);
            this.$el.find('input').unbind('change');
            this.$el.find('input').change(function () {
                var $checkbox = $(this);
                var property = $checkbox.attr('data-for');
                node[property] = $checkbox.is(':checked');
                events.trigger('change', node);
            });
            return events;
        }
    });

    var FieldList = Widget.extend({
        template: 'bi_view_editor.FieldList',
        events: {
            'click .delete-button': 'removeClicked',
            'keyup input[name="description"]': 'keyupDescription'
        },
        start: function () {
            var res = this._super.apply(this, arguments);
            this.contextmenu = new FieldListFieldContextMenu(this);
            this.contextmenu.appendTo(this.$el);
            this.contextmenu_join = new FieldListJoinContextMenu(this);
            this.contextmenu_join.appendTo(this.$el);
            this.$table = this.$el.find('tbody');
            this.mode = null;
            return res;
        },
        setMode: function (mode) {
            if (mode === 'readonly') {
                this.$el.find('input[type="text"]').attr('disabled', true);
                this.$el.find(".delete-button:last").addClass('hidden');
            } else {
                this.$el.find('input[type="text"]').removeAttr('disabled');
                this.$el.find(".delete-button:last").removeClass('hidden');
            }
            this.mode = mode;
        },
        get: function () {
            return $.makeArray(this.$el.find("tbody tr").map(function () {
                var field = $(this).data('field');
                field.description = $(this).find('input[name="description"]').val();
                return field;
            }));
        },
        getModelIds: function () {
            var model_ids = {};
            this.$el.find("tbody tr").each(function () {
                var data = $(this).data('field');
                model_ids[data.table_alias] = data.model_id;
            });
            return model_ids;
        },
        getModelData: function () {
            var model_data = {};
            this.$el.find("tbody tr").each(function () {
                var data = $(this).data('field');
                model_data[data.table_alias] = {
                    model_id: data.model_id,
                    model_name: data.model_name
                };
            });
            return model_data;
        },
        add: function (field) {
            var self = this;
            field.row = typeof field.row === 'undefined' ? false : field.row;
            field.column = typeof field.column === 'undefined' ? false : field.column;
            field.measure = typeof field.measure === 'undefined' ? false : field.measure;
            field.list = typeof field.list === 'undefined' ? true : field.list;
            field._id = typeof field._id === 'undefined' ? _.uniqueId('node_') : field._id;
            if (field.join_node) {
                field.join_left = typeof field.join_left === 'undefined' ? false : field.join_left;
            }

            var i = 0;
            var name = field.name;
            while (this.get().filter(function (item) {
                return item.name === field.name;
            }).length > 0) {
                field.name = name + '_' + i;
                i++;
            }

            // Render table row
            var $html = $(qweb.render(field.join_node ? 'bi_view_editor.JoinListItem' : 'bi_view_editor.FieldListItem', {
                'field': field
            })).data('field', field).contextmenu(function (e) {
                var $item = $(this);
                if (self.mode === 'readonly') {
                    return;
                }
                e.preventDefault();
                self.openContextMenu($item, e.pageX, e.pageY);
            });

            this.$el.find('tbody').append($html);

            this.$el.find(".delete-button").addClass('hidden');
            this.$el.find(".delete-button:last").removeClass('hidden');
            this.order();
        },
        remove: function (id) {
            var $item = this.$el.find('tr[data-id="' + id + '"]');
            $item.remove();
            this.cleanJoinNodes();
            this.$el.find(".delete-button").addClass('hidden');
            this.$el.find(".delete-button:last").removeClass('hidden');
            this.trigger('removed', id);
        },
        set: function (fields) {
            var set_fields = fields;
            if (!set_fields) {
                set_fields = [];
            }
            this.$el.find('tbody tr').remove();
            for (var i = 0; i < set_fields.length; i++) {
                this.add(set_fields[i]);
            }
            this.$el.find(".delete-button").addClass('hidden');
            this.$el.find(".delete-button:last").removeClass('hidden');
        },
        openContextMenu: function ($item, x, y) {
            var field = $item.data('field');
            var contextmenu = field.join_node ? this.contextmenu_join : this.contextmenu;
            // Temporary disable contextmenu for join node (until left join is implemented)
            if (field.join_node) {
                return;
            }
            contextmenu.open(x - 20, y - 20, $item.data('field')).on('change', function (f) {
                $item.data('field', f);
                this.refreshItem($item);
                this.trigger('updated');
            }.bind(this));
        },
        refreshItem: function ($item) {
            var data = $item.data('field');
            var $attributes = $item.find('span[data-for], img[data-for]');
            $.each($attributes, function () {
                var $attribute = $(this);
                var value = data[$attribute.attr('data-for')];
                if (value) {
                    $attribute.removeClass('hidden');
                } else {
                    $attribute.addClass('hidden');
                }
            });
        },
        removeClicked: function (e) {
            var $button = $(e.currentTarget);
            var id = $button.attr('data-id');
            this.remove(id);
        },
        keyupDescription: function () {
            this.trigger('updated');
        },
        cleanJoinNodes: function () {
            var aliases = $.makeArray(this.$el.find("tbody tr").map(function () {
                var data = $(this).data('field');
                return data.table_alias.localeCompare(data.join_node) > 0 ? data.join_node : data.table_alias;
            }));

            this.$el.find("tbody tr").each(function () {
                var data = $(this).data('field');
                if (typeof data.join_node === 'undefined') {
                    return;
                }
                var no_alias = data.table_alias.localeCompare(data.join_node) > 0 &&
                               aliases.indexOf(data.table_alias) === -1;
                if (no_alias ||
                    aliases.indexOf(data.join_node) === -1) {
                    $(this).remove();
                }
            });
        },
        getOrder: function () {
            var items = this.get();
            var ordered = items.sort(function (a, b) {
                var res = a.table_alias.localeCompare(b.table_alias);
                if (res === 0) {
                    var both_join_node = a.join_node && b.join_node;
                    var both_not_join_node = !a.join_node && !b.join_node;
                    if (both_join_node || both_not_join_node) {
                        return 0;
                    } else if (!a.join_node && b.join_node) {
                        if (b.table_alias.localeCompare(b.join_node) > 0) {
                            return 1;
                        }
                        return -1;
                    } else if (a.join_node && !b.join_node) {
                        if (a.table_alias.localeCompare(a.join_node) > 0) {
                            return -1;
                        }
                        return 1;
                    }
                }
                return res;
            });

            var res = [];
            _.each(ordered, function (item) {
                var already_exists = _.findIndex(res, function (f) {
                    return f._id === item._id;
                }) !== -1;
                if (already_exists) {
                    return;
                }
                res.push(item);
                if (item.join_node) {
                    var join_node_fields = _.filter(ordered, function (f) {
                        return f.table_alias === item.join_node && !f.join_node;
                    });
                    res = _.union(res, join_node_fields);
                }
            });
            return res;
        },
        order: function () {
            var order = this.getOrder();
            var $rows = this.$el.find("tbody tr");

            $rows.sort(function (a, b) {
                var a_index = _.findIndex(order, function (item) {
                    return item._id === $(a).data('field')._id;
                });
                var b_index = _.findIndex(order, function (item) {
                    return item._id === $(b).data('field')._id;
                });
                return a_index - b_index;
            }).appendTo(this.$el.find("tbody"));
        }
    });

    return {
        'FieldList': FieldList,
        'FieldListContextMenu': FieldListContextMenu,
        'FieldListFieldContextMenu': FieldListFieldContextMenu,
        'FieldListJoinContextMenu': FieldListJoinContextMenu
    };
});
