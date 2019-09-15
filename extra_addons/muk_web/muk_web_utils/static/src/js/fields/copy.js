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

odoo.define('muk_web_utils.copy', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');
var fields = require('web.basic_fields');
var registry = require('web.field_registry');

var _t = core._t;
var QWeb = core.qweb;

var BinaryFileCopy = fields.FieldBinaryFile.extend({
	init: function () {
        this._super.apply(this, arguments);
        if (!this.field.attachment) {
            throw _.str.sprintf(_t(
        		"The field '%s' must be a binary field with an set " +
        		"attachment flag for the share widget to work."
            ), this.field.string);
        }
        this.accessToken = !!this.nodeOptions.token;
    },
    willStart: function() {
    	var def = this.value && this.res_id ? this._fetchShareUrl() : $.when();
    	return $.when(this._super.apply(this, arguments), def);
    },
    _fetchShareUrl: function() {
    	var self = this;
    	var def = $.Deferred();
    	if (this.accessToken) {
    		this._rpc({
        		model: 'ir.attachment',
        		method: 'search',
                args: [[
                	['res_id', '=', this.res_id],
                	['res_field', '=', this.name],
                	['res_model', '=', this.model],
                ]],
                kwargs: {
                	context: session.user_context,
                },
        	}).then(function(attchments) {
        		self._rpc({
            		model: 'ir.attachment',
            		method: 'generate_access_token',
                    args: attchments
            	}).then(function(access_token) {
            		self.shareUrl = session.url('/web/content', {
            			model: self.model,
            			field: self.name,
            			id: self.res_id,
            			access_token: access_token.shift(),
            		});
            		def.resolve();
            	});
        	});
    	} else {
    		this.shareUrl = session.url('/web/content', {
    			model: self.model,
    			field: self.name,
    			id: self.res_id,
    		});
    		def.resolve();
    	}
    	return def;
    },
    _setUpClipboad: function() {
    	var self = this;
    	var $clipboardBtn = this.$('.mk_copy_binary');
        this.clipboard = new ClipboardJS($clipboardBtn[0], {
            text: function (trigger) {
                return self.shareUrl;
            },
            container: self.$el[0]
        });
        this.clipboard.on('success', function (event) {
            _.defer(function () {
                $clipboardBtn.tooltip('show');
                _.delay(function () {
                    $clipboardBtn.tooltip('hide');
                }, 800);
            });
        });
        $clipboardBtn.click(function(event) {
        	event.stopPropagation();
        });
        $clipboardBtn.tooltip({
        	title: _t('Link Copied!'),
        	trigger: 'manual',
        	placement: 'bottom'
        });
    },
	_renderReadonly: function () {
        this._super.apply(this, arguments);
        this.$el.addClass('mk_field_copy');
        this.$el.append($(QWeb.render('muk_web_utils.BinaryFieldCopy')));
        this._setUpClipboad();
    },
    destroy: function () {
        this._super.apply(this, arguments);
        if (this.clipboard) {
        	this.clipboard.destroy();
        }
    },
});

registry.add('copy_binary', BinaryFileCopy);

return {
	BinaryFileCopy: BinaryFileCopy,
};

});