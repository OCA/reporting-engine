/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Web Utils 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Lesser General Public License as published by
*    the Free Software Foundation, either version 3 of the License, or
*    (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Lesser General Public License for more details.
*
*    You should have received a copy of the GNU Lesser General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_web_utils.ModuleBoolean', function (require) {
"use strict";

var core = require('web.core');
var fields = require('web.basic_fields');
var registry = require('web.field_registry');
var framework = require('web.framework');

var Dialog = require('web.Dialog');
var AbstractField = require('web.AbstractField');

var _t = core._t;
var QWeb = core.qweb;

var ModuleBoolean = fields.FieldBoolean.extend({
	supportedFieldTypes: [],
    events: _.extend({}, AbstractField.prototype.events, {
        'click input': '_onInputClicked',
    }),
    renderWithLabel: function ($label) {
        this.$label = $label;
        this._render();
    },
    _openDialog: function () {
        var buttons = [{
            text: _t("Download"),
            classes: 'btn-primary',
            close: true,
            click: this._confirmRedirect.bind(this),
        }, {
            text: _t("Cancel"),
            close: true,
        }];
        return new Dialog(this, {
            size: 'medium',
            buttons: buttons,
            $content: $('<div>', {
                html: $(QWeb.render('muk_web_utils.MissingModuleDialog')),
            }),
            title: _t("Missing Module"),
        }).open();
    },
    _confirmRedirect: function () {
    	if(this.nodeOptions.url) {
    		framework.redirect(this.nodeOptions.url);
    	} else {
    		var module = this.name.replace("module_", "");
    		framework.redirect("https://apps.odoo.com/apps/modules/browse?search=" + module);
    	}
    },
	_render: function () {
        this._super.apply(this, arguments);
        var $element = this.$label || this.$el;
        $element.append('&nbsp;').append($("<span>", {
            'text': _t("Store"),
            'class': "badge badge-primary oe_inline mk_module_label"
        }));
    },
    _onInputClicked: function (event) {
        if ($(event.currentTarget).prop("checked")) {
            var dialog = this._openDialog();
            dialog.on('closed', this, this._resetValue.bind(this));
        }
    },
    _resetValue: function () {
        this.$input.prop("checked", false).change();
    },
});

registry.add('module_boolean', ModuleBoolean);

return ModuleBoolean;

});