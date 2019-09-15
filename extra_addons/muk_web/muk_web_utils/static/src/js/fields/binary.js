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

odoo.define('muk_web_utils.binary', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var utils = require('web.field_utils');
var fields = require('web.basic_fields');
var registry = require('web.field_registry');

var _t = core._t;
var QWeb = core.qweb;

fields.FieldBinaryFile.include({
	willStart: function () {
		var def = this._rpc({
            route: '/config/muk_web_utils.binary_max_size',
        }).done(function(result) {
        	this.max_upload_size = result.max_upload_size * 1024 * 1024;
        }.bind(this));
		return this._super.apply(this, arguments);
    },
    _renderReadonly: function () {
		this._super.apply(this, arguments);
		var $wrapper = $('<div/>', {
			class: "mk_field_binary_wrapper"
		});
		$wrapper.addClass(this.$el.attr('class'));
		this.$el.removeClass("o_field_widget");
		this.$el.removeClass("o_hidden");
    	$wrapper.append(this.$el);
    	this.setElement($wrapper);
    },
    _renderEdit: function () {
        this._super.apply(this, arguments);
        if (this.nodeOptions && this.nodeOptions.accept) {
        	this.$('input[name="ufile"]').prop("accept", this.nodeOptions.accept);
        }
    },
});

var FieldBinarySize = fields.FieldFloat.extend({
	init: function(parent, name, record) {
        this._super.apply(this, arguments);
        this.nodeOptions = _.defaults(this.nodeOptions, {
        	si: true,
        });
    },
   _formatValue: function (value) {
	   	var options = _.extend({},
	   		this.nodeOptions,
	   		{ data: this.recordData },
	   		this.formatOptions
	   	);
   		return utils.format['binary_size'](value, this.field, options)
   },
});

registry.add('binary_size', FieldBinarySize);

return {
	FieldBinarySize: FieldBinarySize,
};

});
