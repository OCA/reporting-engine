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

odoo.define('muk_web_utils.Dialog', function (require) {
"use strict";

var core = require('web.core');

var Dialog = require('web.Dialog');

var QWeb = core.qweb;
var _t = core._t;

Dialog.input = function (owner, title, options) {
	var $content = $('<main/>');
	var $input = $('<input/>', {
	    type: 'text',
	    class: options && options.input && options.input.class,
	    value: options && options.input && options.input.value,
	});
	$content.append($input);
	var confirm = function(event) {
		if(options && options.confirm_callback) {
			options.confirm_callback.call(self, event, $input.val());
		}
	}
	var buttons = [
        {
            text: _t("Save"),
            classes: 'btn-primary',
            close: true,
            click: confirm,
        },
        {
            text: _t("Cancel"),
            close: true,
            click: options && options.cancel_callback
        }
    ];
    return new Dialog(owner, _.extend({
        size: 'medium',
        buttons: buttons,
        $content: $content,
        title: title,
    }, options)).open({shouldFocusButtons:true});
};


});
