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

odoo.define('muk_web_utils.domain', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var fields = require('web.basic_fields');
var view_dialogs = require('web.view_dialogs');

var _t = core._t;
var QWeb = core.qweb;

fields.FieldDomain.include({
    _onShowSelectionButtonClick: function (e) {
        e.preventDefault();
        new view_dialogs.SelectCreateDialog(this, {
        	context: this.attrs.context || {},
            title: _t("Selected records"),
            res_model: this._domainModel,
            domain: this.value || "[]",
            no_create: true,
            readonly: true,
            disable_multiple_selection: true,
        }).open();
    },
    isValid: function () {
        return (
        		this._isValid && (!this.domainSelector || this.domainSelector.isValid())
        );
    },
});

});
