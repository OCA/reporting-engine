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
 
odoo.define('muk_preview.PreviewContentPDF', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentPDF = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentPDF",
	init: function(parent, url, mimetype, filename) {
    	this._super.apply(this, arguments);
        this.viewer_url = '/web/static/lib/' + 
        	'pdfjs/web/viewer.html?file=' + 
        	encodeURIComponent(this.url);
    },
    renderPreviewContent: function() {
    	var def = $.Deferred();
    	this.$('.mk_preview_pdf iframe').on('load', function () {
    		$(this).contents().find('button#openFile').hide();
    		def.resolve();
        });
    	return def;
    },
    downloadable: false,
    printable: false,
});

registry.add('pdf', PreviewContentPDF);
registry.add('.pdf', PreviewContentPDF);
registry.add('application/pdf', PreviewContentPDF);

return PreviewContentPDF;

});