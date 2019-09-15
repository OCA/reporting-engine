/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Backend Theme 
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

odoo.define('muk_web_theme.FormRenderer', function (require) {
"use strict";

var dom = require('web.dom');
var core = require('web.core');
var config = require("web.config");

var FormRenderer = require('web.FormRenderer');

var _t = core._t;
var QWeb = core.qweb;

FormRenderer.include({
	_renderHeaderButtons: function () {
        var $buttons = this._super.apply(this, arguments);
        if (config.device.isMobile && this.state.model !== "res.config.settings") {
            var $dropdown = $(QWeb.render('muk_web_theme.MenuStatusbarButtons'));
            $buttons.addClass("dropdown-menu").appendTo($dropdown);
            $buttons.children().addClass("dropdown-item");
            return $dropdown;
        }
        return $buttons;
    },
});

});