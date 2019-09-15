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

odoo.define('muk_web_utils.abstract', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var utils = require('web.field_utils');
var fields = require('web.basic_fields');
var registry = require('web.field_registry');

var AbstractField = require('web.AbstractField');

var _t = core._t;
var QWeb = core.qweb;

AbstractField.include({
	isFocusable: function () {
    	if(!!this.attrs.skip_focus){
    		return false;
    	}
        return this._super.apply(this, arguments);
    },
});

});
