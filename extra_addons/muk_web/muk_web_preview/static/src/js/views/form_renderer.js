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

odoo.define('muk_web_preview.FormRenderer', function (require) {
"use strict";

var core = require('web.core');
var config = require('web.config');
var session = require('web.session');
var pyUtils = require('web.py_utils');

var FormRenderer = require('web.FormRenderer');

FormRenderer.include({
	_renderView: function () {
        return this._super.apply(this, arguments).then(function () {
        	if (!this.$previewSidebar || config.device.size_class < config.device.SIZES.XXL || 
        		(this.$previewSidebar && this.$previewSidebar.hasClass('o_invisible_modifier'))) {
                this.$el.removeClass("mk_preview_sidebar_active");
            } else {
            	var $sheet = this.$('.o_form_sheet_bg');
                this.$previewSidebar.insertAfter($sheet);
                if (this.chatter) {
                    this.chatter.$el.appendTo($sheet);
                    this.chatterPositionChanged = true;
                }
                this.$el.addClass("mk_preview_sidebar_active");
            }
        }.bind(this));
    },
    _renderNode: function (node) {
        if (node.tag === 'div' && node.attrs.class === 'mk_preview_sidebar') {
        	this.$previewSidebar = $('<div>', {
        		'class': 'mk_preview_sidebar',
        		'width': this.previewSidebarWidth || '600px',
        	});
			var childs = _.each(node.children, function (child) {
				this.$previewSidebar.append(this._renderNode(child));
            }, this);
			this.$previewSidebar.resizable({
                handles: 'w',
                minWidth: 400,
                maxWidth: 850,
                resize: function (event, ui) {
                    this.previewSidebarWidth = ui.size.width;
                }.bind(this),
            });
        	this._handleAttributes(this.$previewSidebar, node);
			this._registerModifiers(node, this.state, this.$previewSidebar);
        	return this.$previewSidebar;
        } else {
            return this._super.apply(this, arguments);
        }
    },
});

});