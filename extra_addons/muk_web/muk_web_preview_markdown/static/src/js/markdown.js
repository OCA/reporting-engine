/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview Markdown 
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

odoo.define('muk_preview_markdown.PreviewContentMarkdown', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentMarkdown = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentMarkdown",    
	jsLibs: [
		'/muk_web_preview_markdown/static/lib/showdown/showdown.js',
    ],
	willStart: function() { 
		var def = $.ajax({
		  url: this.url,
		  dataType: "text",
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		}).done(function(text) {
			this.markdown = text;
		}.bind(this));
		return $.when(this._super.apply(this, arguments), def);
    },
    renderPreviewContent: function() {
    	var converter = new showdown.Converter();
    	this.$('.mk_preview_markdown').html(
    		converter.makeHtml(this.markdown)
    	);
    	return this._super.apply(this, arguments);
    },
    downloadable: true,
    printable: true,
});

registry.add('md', PreviewContentMarkdown);
registry.add('.md', PreviewContentMarkdown);
registry.add('text/markdown', PreviewContentMarkdown);

return PreviewContentMarkdown;

});
