/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview ReStructuredText 
*    (see https://mukit.at).
*
*    This program is free software: you can redistribute it and/or modify
*    it under the terms of the GNU Affero General Public License as
*    published by the Free Software Foundation, either version 3 of the
*    License, or (at your option) any later version.
*
*    This program is distributed in the hope that it will be useful,
*    but WITHOUT ANY WARRANTY; without even the implied warranty of
*    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
*    GNU Affero General Public License for more details.
*
*    You should have received a copy of the GNU Affero General Public License
*    along with this program. If not, see <http://www.gnu.org/licenses/>.
*
**********************************************************************************/

odoo.define('muk_preview_markdown.PreviewContentReStructuredText', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentReStructuredText = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentReStructuredText",    
	willStart: function() { 
		var def = $.Deferred();
		this._downloadFile().done(function(text) {
			this._parseFile(text).done(function(html) {
				this.html = html;
				def.resolve();
			}.bind(this));
		}.bind(this));
		return $.when(this._super.apply(this, arguments), def);
    },
    renderPreviewContent: function() {
    	this.$('.mk_preview_rst').html(this.html);
    	return this._super.apply(this, arguments);
    },
    _downloadFile: function() {
		return $.ajax({
			url: this.url,
			dataType: "text",
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		});
    },
    _parseFile: function(content) {
		return $.ajax({
			url: '/preview/convert/rst',
			data: { 
				'content': content,
			},
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		});
    },
    downloadable: true,
    printable: true,
});

registry.add('rst', PreviewContentReStructuredText);
registry.add('.rst', PreviewContentReStructuredText);
registry.add('text/x-rst', PreviewContentReStructuredText);

return PreviewContentReStructuredText;

});
