/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview CSV 
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

odoo.define('muk_preview_markdown.PreviewContentCSV', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentCSV = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentCSV",    
	cssLibs: [
		'/muk_web_preview_csv/static/lib/pikaday/pikaday.css',
		'/muk_web_preview_csv/static/lib/handsontable/handsontable.css',
    ],
    jsLibs: [
        '/muk_web_preview_csv/static/lib/papaparse/papaparse.js',
        '/muk_web_preview_csv/static/lib/numbro/numbro.js',
        '/muk_web_preview_csv/static/lib/pikaday/pikaday.js',
        '/muk_web_preview_csv/static/lib/handsontable/handsontable.js',
    ],
    willStart: function() { 
		var def = $.Deferred();
		this._super.apply(this, arguments).then(function() {
			Papa.parse(this.url, {
	            download: true,
	            dynamicTyping: true,
	            complete: function(results) {
	            	this.csv = results.data;
	            	def.resolve();
	            }.bind(this),
			});
		}.bind(this));
		return def;
    },
    renderPreviewContent: function() {
    	console.log(this.csv);
    	this.$('.mk_preview_csv').handsontable({
		    data: this.csv,
		    rowHeaders: true,
		    colHeaders: true,
		    stretchH: 'all',
		    readOnly: true,
		    columnSorting: true,
		    autoColumnSize: true,
		});
    	return this._super.apply(this, arguments);
    },
    downloadable: true,
    printable: false,
});


registry.add('csv', PreviewContentCSV);
registry.add('.csv', PreviewContentCSV);
registry.add('text/csv', PreviewContentCSV);
registry.add('application/csv', PreviewContentCSV);
registry.add('text/comma-separated-values', PreviewContentCSV);

return PreviewContentCSV;

});
