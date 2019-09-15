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

odoo.define('muk_web_preview.binary', function(require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var session = require('web.session');
var fields = require('web.basic_fields');
var registry = require('web.field_registry');
var field_utils = require('web.field_utils');

var PreviewManager = require('muk_preview.PreviewManager');
var PreviewDialog = require('muk_preview.PreviewDialog');

var _t = core._t;
var QWeb = core.qweb;

fields.FieldBinaryFile.include({
	events: _.extend({}, fields.FieldBinaryFile.prototype.events, {
		"click .mk_field_preview_button": "_onPreviewButtonClick",
    }),
	_renderReadonly: function () {
		this._super.apply(this, arguments);
		var $button = $('<button/>', {
			class: 'mk_field_preview_button',
			type: 'button',
			html: '<i class="fa fa-file-text-o"></i>',
		});
    	this.$el.prepend($button);
    },
    _onPreviewButtonClick: function(event) {
        var filename_fieldname = this.attrs.filename;
        var last_update =  this.recordData.__last_update;
        var mimetype = this.recordData['mimetype'] || null;
        var filename = this.recordData[filename_fieldname] || null;
        var unique = last_update && field_utils.format.datetime(last_update);
        var binary_url = session.url('/web/content', {
            model: this.model,
            id: JSON.stringify(this.res_id),
            data: utils.is_bin_size(this.value) ? null : this.value,
            unique: unique ? unique.replace(/[^0-9]/g, '') : null,
            filename_field: filename_fieldname,
            filename: filename,
            field: this.name,
            download: true,
        });
        var preview = new PreviewDialog(
    		this, [{
    			url: binary_url,
    			filename: filename,
    			mimetype: mimetype,
    		}], 0
        );
        preview.appendTo($('body'));
    	event.stopPropagation();
    	event.preventDefault();
    },
});

var FieldBinaryPreview = fields.FieldBinaryFile.extend({
    template: 'muk_preview.FieldBinaryPreview',
	_renderReadonly: function () {
		this._renderPreview();
    },
    _renderEdit: function () {
    	if (this.value) {
    		this.$('.mk_field_preview_container').removeClass("o_hidden");
        	this.$('.o_select_file_button').first().addClass("o_hidden");
    		this._renderPreview();	
        } else {
        	this.$('.mk_field_preview_container').addClass("o_hidden");
        	this.$('.o_select_file_button').first().removeClass("o_hidden");
        }
    },
    _renderPreview: function() {
    	this.$('.mk_field_preview_container').empty();
    	var filename_fieldname = this.attrs.filename;
        var last_update =  this.recordData.__last_update;
        var filename = this.recordData[filename_fieldname] || null;
        var unique = last_update && field_utils.format.datetime(last_update);
    	var binary_url = session.url('/web/content', {
            model: this.model,
            id: JSON.stringify(this.res_id),
            data: utils.is_bin_size(this.value) ? null : this.value,
            unique: unique ? unique.replace(/[^0-9]/g, '') : null,
            filename_field: filename_fieldname,
            filename: filename,
            field: this.name,
            download: true,
        });
    	var manager = new PreviewManager(
    		this, [{
    			url: binary_url,
    			filename: filename,
    			mimetype: undefined,
    		}], 0
        );
    	manager.appendTo(this.$('.mk_field_preview_container'));
    },
    on_save_as: function (event) {
    	event.stopPropagation();
    },
});

registry.add('binary_preview', FieldBinaryPreview);

return FieldBinaryPreview;

});
