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

odoo.define('muk_web_utils.image', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var fields = require('web.basic_fields');

var _t = core._t;
var QWeb = core.qweb;

fields.FieldBinaryImage.include({
	willStart: function () {
		var def = this._rpc({
            route: '/config/muk_web_utils.binary_max_size',
        }).done(function(result) {
        	this.max_upload_size = result.max_upload_size * 1024 * 1024;
        }.bind(this));
		return this._super.apply(this, arguments);
    },
	_render: function () {
		this._super.apply(this, arguments);
		this.$('.mk_field_image_wrapper').remove();
		this.$('img').wrap($('<div/>', {
			class: "mk_field_image_wrapper"
		}));
		var $wrapper = $('.mk_field_image_wrapper');
		var width = this.nodeOptions.size ? 
			this.nodeOptions.size[0] : this.attrs.width;
        var height = this.nodeOptions.size ? 
        	this.nodeOptions.size[1] : this.attrs.height;
        $wrapper.css('min-width', (width || 50) + 'px');
        $wrapper.css('min-height', (height || 50) + 'px');
	},
});

});
