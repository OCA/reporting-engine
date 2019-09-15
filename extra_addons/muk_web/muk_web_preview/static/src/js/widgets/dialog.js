/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview 
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

odoo.define('muk_preview.PreviewDialog', function (require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var session = require('web.session');

var PreviewManager = require('muk_preview.PreviewManager');

var QWeb = core.qweb;
var _t = core._t;

var PreviewDialog = PreviewManager.extend({
    template: "muk_preview.PreviewDialog",
	events: _.extend({}, PreviewManager.prototype.events, {
		'click .mk_preview_maximize_btn': '_onMaximizeClick',
		'click .mk_preview_minimize_btn': '_onMinimizeClick',
	}),
    start: function () {
        this.$el.modal('show');
        this.$el.on('hidden.bs.modal', _.bind(this._onDestroy, this));
        this.$('[data-toggle="tooltip"]').tooltip({delay: 0});
        return this._super.apply(this, arguments); 
    },
    destroy: function () {
        if (this.isDestroyed()) {
            return;
        }
        this.$el.modal('hide');
        this.$el.remove();
        return this._super.apply(this, arguments);
    },
    _renderPreview: function (element) {
    	this._super.apply(this, arguments);
    	this.$('.modal-title').text(this.activeFile.filename || "Preview");
    },
    _onDestroy: function () {
        this.destroy();
    },
    _onMaximizeClick: function(event) {
    	this.$('.mk_preview_dialog').addClass("mk_preview_maximize");
    },
    _onMinimizeClick: function(event) {
    	this.$('.mk_preview_dialog').removeClass("mk_preview_maximize");
    },
});


return PreviewDialog;

});