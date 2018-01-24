odoo.define('bi_view_editor', function (require) {
"use strict";

    var Core = require("web.core");
    var FormCommon = require('web.form_common');
    var Model = require('web.Model');
    var Data = require('web.data');
    var Widget = require('web.Widget');
    var Dialog = require("web.Dialog");
    var _t = Core._t;

    var JoinNodePopup = Widget.extend({
        template: "JoinNodePopup",
        start: function() {
            var self = this;
        },

        display_popup: function(choices, model_data, callback, callback_data) {
            var self = this;
            this.renderElement();
            var joinnodes = this.$el.find('#join-nodes');
            joinnodes.empty();
            for (var i=0; i<choices.length; i++) {
                var description = "";
                if (choices[i].join_node !== -1 && choices[i].table_alias !== -1) {
                    description = _t("Use the field on model") + " <b>" + model_data[choices[i].table_alias].model_name + "</b>";
                } else {
                    var new_str = "";
                    if (choices[i].join_node !== -1) {
                        new_str = "<b>" + _t("new") + "</b> ";
                    }
                    description = _t("<b>Join</b> using the field") + " <u><b>" + choices[i].description + "</b></u> " + _t("on ") + new_str + _t("model") +" <b>" + choices[i].model_name + "</b>";
                }
                joinnodes.append($('<a><input type="radio">' + description+ '</a>')
                                 .data('idx', i)
                                 .wrap('<p></p>')
                                 .parent());
            }
            var dialog = new Dialog(this, {
                dialogClass: 'oe_act_window',
                title: _t("Choose join node"),
                $content: this.$el,
                buttons: [{text: _t("Cancel"),
                           classes: "btn-default o_form_button_cancel",
                           close: true
                           }]
            }).open();

            joinnodes.find('a').click(function() {
                callback(callback_data, choices[$(this).data('idx')]);
                dialog.close();
            });

            this.start();
        }
    });

    var BiViewEditor = FormCommon.AbstractField.extend({
        template: "BVEEditor",
        activeModelMenus: [],
        currentFilter: "",
        init: function() {
            this._super.apply(this, arguments);
        },
        start: function() {
            this._super();
            this.on("change:effective_readonly", this, function() {
                this.display_field();
                this.render_value();
            });
            this.display_field();
            this.render_value();
        },
        display_field: function () {
            var self = this;
            this.$el.find(".body .right").droppable({
                accept: "div.class-list div.field",
                drop: function (event, ui) {
                    self.add_field(ui.draggable);
                    ui.draggable.draggable('option', 'revert', false );
                }
            });
            if (!this.get("effective_readonly")) {
                this.$el.find('.search-bar').attr('disabled', false);
                this.$el.find('.class-list').css('opacity', '1');
                this.$el.find('.class-list .class').css('cursor', 'pointer');
                this.$el.find(".body .right").droppable("option", "disabled", false);
                this.$el.find('#clear').css('display', 'inline-block').click(function () {
                    self.set_fields([]);
                    self.internal_set_value('[]');
                });
                this.$el.find('.search-bar input').keyup(function(e) {
                    //Local filter
                    self.filter($(this).val());
                });
            } else {
                this.$el.find(".body .right").droppable("option", "disabled", true);
                this.$el.find('#clear').css('display', 'none');
                this.$el.find('.search-bar').attr('disabled', true);
                this.$el.find('.class-list').css('opacity', '.35');
                this.$el.find('.class-list .class').css('cursor', 'default');
            }
        },
        filter: function(val) {
            val = (typeof val !== 'undefined') ? val.toLowerCase() : this.currentFilter;
            this.currentFilter = val;
            this.$el.find(".class-list .class-container").each(function() {
                var modelData = $(this).find(".class").data('model-data');
                //TODO: filter on all model fields (name, technical name, etc)

                if(typeof modelData === 'undefined' || (modelData.name.toLowerCase().indexOf(val) === -1 && modelData.model.toLowerCase().indexOf(val) === -1))
                    $(this).hide();
                else
                    $(this).show();
            });
        },
        get_field_icons: function(field) {
            var icons = "";
            if(field.column)
                icons += "<span class='fa fa-columns' title='Column'></span> ";
            if(field.row)
                icons += "<span class='fa fa-bars' title='Row'></span> ";
            if(field.measure)
                icons += "<span class='fa fa-bar-chart-o' title='Measure'></span> ";
            if(field.list)
                icons += "<span class='fa fa-list' title='List'></span> ";

            return icons;
        },
        update_field_view: function(row) {
            row.find("td:nth-child(3)").html(this.get_field_icons(row.data('field-data')));
        },
        render_value: function() {
            this.set_fields(JSON.parse(this.get('value')));
        },
        load_classes: function(scrollTo) {
            scrollTo = (typeof scrollTo === 'undefined') ? false : scrollTo;
            var self = this;
            var model = new Model("ir.model");
            if (this.$el.find(".field-list tbody tr").length > 0) {
                model.call("get_related_models", [this.get_model_ids()], { context: new Data.CompoundContext() }).then(function(result) {
                    self.show_classes(result);
                });
            } else {
                model.call("get_models", { context: new Data.CompoundContext() }).then(function(result) {
                    self.show_classes(result);
                });
            }
        },
        show_classes: function (result) {
            var self = this;
            var model = new Model("ir.model");
            self.$el.find(".class-list .class").remove();
            self.$el.find(".class-list .field").remove();
            var css = this.get('effective_readonly') ? 'cursor: default' : 'cursor: pointer';
            function addField() {
                if (!self.get("effective_readonly")) {
                    self.add_field($(this));
                }
            }
            function clickHandler(evt) {
                if(self.get("effective_readonly")) return;
                var classel = $(this);
                if (classel.data('bve-processed')) {
                    classel.parent().find('.field').remove();
                    classel.data('bve-processed', false);
                    var index = self.activeModelMenus.indexOf(classel.data('model-data').id);
                    if(index !== -1) self.activeModelMenus.splice(index, 1);
                } else {
                    self.activeModelMenus.push(classel.data('model-data').id);
                    model.call("get_fields", [classel.data('model-data').id], { context: new Data.CompoundContext() }).then(function(result) {
                        for (var i = 0; i < result.length; i++) {
                            classel.find("#bve-field-" + result[i].name).remove();
                            self._render_field(self, i, result, classel, addField)
                        }
                    });
                    $(this).data('bve-processed', true);
                }
            }
            function renderFields(result) {
                console.log(result);
                var item = self.$el.find(".class-list #bve-class-" + result[0].model_id);
                for (var o = 0; o < result.length; o++) {
                    self._render_field(self, o, result, item, addField)
                }
                item.data('bve-processed', true);
            }
            for (var i = 0; i < result.length; i++) {
                var item = $("<div style=\"" + css + "\" class=\"class\" title=\"" + result[i].model  + "\" id=\"bve-class-" + result[i].id + "\">" + result[i].name + "</div>")
                            .data('model-data', result[i])
                            .click(clickHandler)
                            .wrap("<div class=\"class-container\"></div>").parent();
                self.$el.find(".class-list").append(item);

                var index = self.activeModelMenus.indexOf(item.find(".class").data('model-data').id);
                if(index !== -1 && !self.get("effective_readonly")) {
                    model.call("get_fields", [self.activeModelMenus[index]], { context: new Data.CompoundContext() }).then(renderFields);
                }
                self.filter();
            }

        },
        _render_field(_self, _index, _result, _item, _addField) {
            if(_self.$el.find(".field-list tbody [name=label-" + _result[_index].id + "]").length > 0) return;
            _item.after($("<div class=\"field\" title=\"" + _result[_index].name + "\" id=\"bve-field-" + _result[_index].name + "\">" + _result[_index].description + "</div>")
                          .data('field-data', _result[_index])
                          .click(_addField)
                          .draggable({
                              'revert': 'invalid',
                              'scroll': false,
                              'helper': 'clone',
                              'appendTo': 'body',
                              'containment': 'window'
                          })
                      );
        },
        set_checkbox: function(check, identifier, _contextMenu) {
            if(check)
                _contextMenu.find(identifier).attr('checked', true);
            else
                _contextMenu.find(identifier).attr('checked', false);
        },
        _false_if_undefined: function(to_check) {
            if (typeof to_check === 'undefined') return false;
            return to_check;
        },
        _true_if_undefined: function(to_check) {
            if (typeof to_check === 'undefined') return true;
            return to_check;
        },
        add_field_to_table: function(data, options) {
            var self = this;
            data.row = self._false_if_undefined(data.row);
            data.column = self._false_if_undefined(data.column);
            data.measure = self._false_if_undefined(data.measure);
            data.list = self._true_if_undefined(data.list);

            var n = 1;
            var name = data.name;
            function checkNameMatches(el) { return el.name === data.name;}
            while ($.grep(self.get_fields(), checkNameMatches).length > 0) {
                data.name = name + '_' + n;
                n += 1;
            }
            var classes = "";
            if (typeof data.join_node !== 'undefined') {
                classes = "join-node displaynone";
            }
            var delete_button = "";
            var disabled = " disabled=\"disabled\" ";
            if (!this.get("effective_readonly")) {
                delete_button = "<span id=\"delete-" + data.id + "\" class=\"delete-button fa fa-trash-o\"/>";
                disabled = "";
            }

            self.$el.find(".field-list tbody")
                .append($("<tr class=\"" + classes + "\"><td><input " + disabled + "title=\"" + data.name + " (" + data.model + ")\" type=\"text\" name=\"label-" + data.id + "\" value=\"" + data.description + "\"/></td><td>" + data.model_name + "</td><td>" + self.get_field_icons(data) + "</td><td>" + delete_button + "</td></tr>")
                .data('field-data', data)
                .contextmenu(function(e) {
                    e.preventDefault();
                    if (self.get("effective_readonly")) return;
                    var target = $(e.currentTarget);
                    var currentFieldData = target.data('field-data');

                    var contextMenu = self.$el.find(".context-menu");
                    contextMenu.css("left", e.pageX + "px");
                    contextMenu.css("top", e.pageY + "px");
                    contextMenu.mouseleave(function() {
                        contextMenu.hide();
                    });
                    contextMenu.find("li").hover(function() {
                        $(this).find("ul").css("color", "#000");
                        $(this).find("ul").show();
                    }, function() {
                        $(this).find("ul").hide();
                    });


                    //Set checkboxes
                    self.set_checkbox(currentFieldData.column, '#column-checkbox', contextMenu);
                    self.set_checkbox(currentFieldData.row, '#row-checkbox', contextMenu);
                    self.set_checkbox(currentFieldData.measure, '#measure-checkbox', contextMenu);
                    self.set_checkbox(currentFieldData.list, '#list-checkbox', contextMenu);

                    var to_disable = false;
                    if(currentFieldData.type === "float" || currentFieldData.type === "integer" || currentFieldData.type === "monetary") to_disable = true;
                    var identifiers = [['#column-checkbox', 'column', to_disable], ['#row-checkbox', 'row', to_disable], ['#measure-checkbox', 'measure', !to_disable], ['#list-checkbox', 'list', false]];
                    identifiers.forEach(function (element) {
                        contextMenu.find(element[0]).attr('disabled', element[2]);
                    });

                    //Add change events
                    identifiers.forEach(function (element) {
                        contextMenu.find(element[0]).unbind("change");
                        contextMenu.find(element[0]).change(function() {
                            currentFieldData[element[1]] = $(this).is(":checked");
                            target.data('field-data', currentFieldData);
                            self.update_field_view(target);
                            self.internal_set_value(JSON.stringify(self.get_fields()));
                        });

                    });
                    contextMenu.show();

                    $(document).mouseup(function (e) {
                        var container = $(".context-menu");

                        // if the target of the click isn't the container nor a descendant of the container
                        if (!container.is(e.target) && container.has(e.target).length === 0)
                        {
                            container.hide();
                        }
                    });

                })
             );

            self.$el.find('.delete-button').unbind("click");
            self.$el.find('.delete-button').click(function() {
                $(this).closest('tr').remove();
                self.clean_join_nodes();
                self.internal_set_value(JSON.stringify(self.get_fields()));
                self.load_classes();
                return false;
            });
        },
        clean_join_nodes: function () {
            var aliases = $.makeArray(this.$el.find(".field-list tbody tr").map(function (idx, el) {
                var d = $(this).data('field-data');
                return d.table_alias;
            }));

            this.$el.find(".field-list tbody tr").each(function (idx, el) {
                var d = $(this).data('field-data');
                if (typeof d.join_node !== 'undefined' && aliases.indexOf(d.join_node) === -1) {
                    $(this).remove();
                }
            });
        },
        get_model_ids: function () {
            var model_ids = {};
            this.$el.find(".field-list tbody tr").each(function (idx, el) {
                var d = $(this).data('field-data');
                model_ids[d.table_alias] = d.model_id;
            });
            return model_ids;
        },
        get_model_data: function () {
            var model_data = {};
            this.$el.find(".field-list tbody tr").each(function (idx, el) {
                var d = $(this).data('field-data');
                model_data[d.table_alias] = {model_id: d.model_id, model_name: d.model_name};
            });
            return model_data;
        },
        get_table_alias: function(field) {
            if (typeof field.table_alias !== 'undefined') {
                return field.table_alias;
            } else {
                var model_ids = this.get_model_ids();
                var n = 0;
                while (typeof model_ids["t" + n] !== 'undefined') n++;
                return "t" + n;
            }
        },
        add_field_and_join_node: function(field, join_node) {
            var self = this;

            var go_to_else = true;
            if (join_node.join_node === -1 || join_node.table_alias === -1){
                go_to_else = false;
                field.table_alias = self.get_table_alias(field);
                if (join_node.join_node === -1) join_node.join_node = field.table_alias;
                else join_node.table_alias = field.table_alias;
                self.add_field_to_table(join_node);
            }
            else field.table_alias = join_node.table_alias;

            self.add_field_to_table(field);
            self.internal_set_value(JSON.stringify(self.get_fields()));
            self.load_classes(field);
        },
        add_field: function(field) {
            var data = field.data('field-data');
            var model = new Model("ir.model");
            var model_ids = this.get_model_ids();
            var field_data = this.get_fields();
            var self = this;
            model.call('get_join_nodes', [field_data, data], {context: new Data.CompoundContext()}).then(function(result) {

                if (result.length === 1) {
                    self.add_field_and_join_node(data, result[0]);
                    self.internal_set_value(JSON.stringify(self.get_fields()));
                    //self.load_classes(data);
                } else if (result.length > 1) {
                    var pop = new JoinNodePopup(self);
                    pop.display_popup(result, self.get_model_data(), self.add_field_and_join_node.bind(self), data);
                } else {
                    // first field and table only.
                    var table_alias = self.get_table_alias(data);
                    data.table_alias = table_alias;
                    self.add_field_to_table(data);
                    self.internal_set_value(JSON.stringify(self.get_fields()));
                    self.load_classes(data);
                }
            });
        },
        get_fields: function() {
            return $.makeArray(this.$el.find(".field-list tbody tr").map(function (idx, el) {
                var d = $(this).data('field-data');
                d.description = $("input[name='label-" + d.id + "']").val();
                return d;
            }));
        },
        set_fields: function(values) {
            this.activeModelMenus = [];
            if (!values) {
                values = [];
            }
            this.$el.find('.field-list tbody tr').remove();
            for(var i = 0; i < values.length; i++) {
                this.add_field_to_table(values[i]);
            }
            this.load_classes();
        }
    });
    Core.form_widget_registry.add('BVEEditor', BiViewEditor);

});
