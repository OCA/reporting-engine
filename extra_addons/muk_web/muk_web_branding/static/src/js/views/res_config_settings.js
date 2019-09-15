/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Web Branding 
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

odoo.define('muk_web_branding.settings', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var settings = require('base.settings');

var _t = core._t;
var QWeb = core.qweb;

settings.Renderer.include({
	_render: function () {
        var res = this._super.apply(this, arguments);
        $.each(this.$('.o_settings_container'), function() {
        	if($(this).children(':not(.o_hidden)').length === 0) {
            	$(this).prev().addClass('o_hidden');
            	$(this).addClass('o_hidden');
        	}
		});
        return res;
    },
});

});