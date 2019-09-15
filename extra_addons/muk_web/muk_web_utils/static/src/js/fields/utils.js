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

odoo.define('muk_web_utils.field_utils', function(require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var utils = require('web.field_utils');

var _t = core._t;
var QWeb = core.qweb;

function formatBinarySize(value, field, options) {
	options = _.defaults(options || {}, {
    	si: true,
    });
	var thresh = options.si ? 1000 : 1024;
    if(Math.abs(value) < thresh) {
        return utils.format['float'](value, field, options) + ' B';
    }
    var units = options.si
        ? ['KB','MB','GB','TB','PB','EB','ZB','YB']
        : ['KiB','MiB','GiB','TiB','PiB','EiB','ZiB','YiB'];
    var unit = -1;
    do {
        value /= thresh;
        ++unit;
    } while(Math.abs(value) >= thresh && unit < units.length - 1);
    return utils.format['float'](value, field, options) + ' ' + units[unit];
}

utils.format.binary_size = formatBinarySize;

});
