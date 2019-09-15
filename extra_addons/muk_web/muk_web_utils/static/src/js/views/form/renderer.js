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

odoo.define('muk_web_utils.FormRenderer', function (require) {
"use strict";

var core = require('web.core');

var FormRenderer = require('web.FormRenderer');

var _t = core._t;
var QWeb = core.qweb;

FormRenderer.include({
    _updateView: function ($newContent) {
    	this._super.apply(this, arguments);
    	_.each(this.allFieldWidgets[this.state.id], function (widget) {
            if (widget.attrs.widget === 'module_boolean') {
                var inputID = this.idsForLabels[widget.name];
                var $widgets = this.$('.o_field_widget[name=' + widget.name + ']');
                var $label = inputID ? this.$('.o_form_label[for=' + inputID + ']') : $();
                widget.renderWithLabel($label.eq($widgets.index(widget.$el)));
            }
        }, this);
    }
});

});