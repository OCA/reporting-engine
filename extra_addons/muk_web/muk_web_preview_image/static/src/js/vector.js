/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview Image 
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

odoo.define('muk_preview_markdown.PreviewContentVector', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentVector = AbstractPreviewContent.extend({
	events: _.extend({}, AbstractPreviewContent.prototype.events, {
		'click .zoom-plus': '_onZoomIn',
		'click .zoom-minus': '_onZoomOut',
		'click .zoom-reset': '_onReset',
	}),
	template: "muk_preview.PreviewContentVector",    
    jsLibs: [
        '/muk_web_preview_image/static/lib/svg-pan-zoom/svg-pan-zoom.js',
    ],
	willStart: function() { 
		var def = $.ajax({
		  url: this.url,
		  dataType: "text",
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		}).done(function(vector) {
			this.vector = vector;
		}.bind(this));
		return $.when(this._super.apply(this, arguments), def);
    },
    renderPreviewContent: function() {
    	this.$('.vector-content').html(this.vector);
    	this.svgPanZoom = this.$("svg").svgPanZoom({
    	    events: {
    	        mouseWheel: true,
    	        doubleClick: true,
    	        drag: true,
    	        dragCursor: "move",
    	    },
    	    animationTime: 300,
    	    zoomFactor: 0.1,
    	    maxZoom: 5, 
    	    panFactor: 100, 
    	});
    	return this._super.apply(this, arguments);
    },
    _onZoomIn: function(event) {
    	console.log(this.svgPanZoom);
    	this.svgPanZoom.zoomIn();
    },
    _onZoomOut: function(event) {
    	this.svgPanZoom.zoomOut();
    },
    _onReset: function(event) {
    	this.svgPanZoom.reset();
    },
    downloadable: true,
    printable: true,
});



registry.add('svg', PreviewContentVector);
registry.add('.svg', PreviewContentVector);
registry.add('image/svg+xml', PreviewContentVector);

return PreviewContentVector;

});
