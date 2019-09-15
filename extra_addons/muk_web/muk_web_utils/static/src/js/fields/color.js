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

odoo.define('muk_web_utils.color', function (require) {
"use strict";

var core = require('web.core');
var fields = require('web.basic_fields');
var registry = require('web.field_registry');
var colorpicker = require('web.colorpicker');

var AbstractField = require('web.AbstractField');

var _t = core._t;
var QWeb = core.qweb;

var FieldColor = fields.InputField.extend({
	events: _.extend({}, fields.InputField.prototype.events, {
		"click .mk_field_color_button": "_onCustomColorButtonClick",
    }),
    template: "muk_web_utils.FieldColor",
    supportedFieldTypes: ['char'],
    start: function() {
    	this.$input = this.$('.mk_field_color_input');
    	return this._super.apply(this, arguments);
    },
    _renderEdit: function () {
        this.$('.mk_field_color_input').val(
        	this._formatValue(this.value)
        );
        this.$('.mk_field_color_input').css({
        	'background-color': this._formatValue(this.value),
        });
    },
    _renderReadonly: function () {
        this.$el.text(this._formatValue(this.value));
        this.$el.css({'color': this._formatValue(this.value)});
    },
    _doAction: function() {
    	this._super.apply(this, arguments);
    	this.$('.mk_field_color_input').css({
        	'background-color': this._getValue(),
        });
    },
    _formatValue: function (value) {
    	return value;
    },
    _parseValue: function (value) {
    	if((/(^#[0-9A-F]{6}$)|(^#[0-9A-F]{3}$)/i).test(value)) {
    		return value;
    	} else {
    		throw new Error(_.str.sprintf(_t("'%s' is not a correct color value"), value));
    	}
    },
    _onCustomColorButtonClick: function () {
        var ColorpickerDialog = new colorpicker(this, {
        	dialogClass: 'mk_field_color_picker',
        	defaultColor: this._getValue(),
        });
        ColorpickerDialog.on('colorpicker:saved', this, function (event) {
        	this.$input.val(event.data.hex);
        	this._doAction();
        });
        ColorpickerDialog.open();
    },
});

var FieldColorIndex = AbstractField.extend({
    events: _.extend({}, AbstractField.prototype.events, {
        'change': '_onChange',
    }),
	template: 'muk_web_utils.FieldColorIndex',
    supportedFieldTypes: ['integer'],
    isSet: function () {
    	return this.value === 0 || this._super.apply(this, arguments);
    },
    getFocusableElement: function () {
        return this.$el.is('select') ? this.$el : $();
    },
    _renderEdit: function () {
        this.$el.addClass('mk_color_index_' + this.value);
        this.$('option[value="' + this.value + '"]').prop('selected', true);
    },
    _renderReadonly: function () {
        this.$el.addClass('mk_color_index_' + this.value);
        this.$el.empty().text('Color ' + this._formatValue(this.value));
    },
    _onChange: function (event) {
    	this.$el.removeClass(function (index, className) {
    	    return (className.match (/(^|\s)mk_color_index_\S+/g) || []).join(' ');
    	});
    	this.$el.addClass('mk_color_index_' + this.$el.val());
    	this._setValue(this.$el.val());
    },
    _parseValue: function (value) {
    	if(0 > value || value > 12) {
    		throw new Error(_.str.sprintf(_t("'%s' is not a correct color index (0-12)"), value));
    	} 
    	return value;
    },
});

registry.add('color', FieldColor);
registry.add('color_index', FieldColorIndex);

return {
	FieldColor: FieldColor,
	FieldColorIndex: FieldColorIndex,
};

});