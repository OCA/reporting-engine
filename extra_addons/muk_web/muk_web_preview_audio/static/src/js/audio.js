/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview Audio 
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

odoo.define('muk_preview_markdown.PreviewContentAudio', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentAudio = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentAudio",    
	jsLibs: [
		'/muk_web_preview_audio/static/lib/visualizer/visualizer.js',
    ],
    mimetypeMap: {
		'.wav': 'audio/wav', '.ogg': 'audio/ogg', '.mp3': 'audio/mpeg',
		'wav': 'audio/wav', 'ogg': 'audio/ogg', 'mp3': 'audio/mpeg',
	},
	init: function(parent, url, mimetype, filename) {
    	this._super.apply(this, arguments);
    	if(this.mimetype === 'application/octet-stream') {
    		var extension = this.filename.split('.').pop();
    		this.mimetype = this.mimetypeMap[extension];
    	}
    },
    renderPreviewContent: function() {
    	this.visualizer = new Visualizer(
    		this.$('audio'),
    		this.$('.visualizer'),
    		this.$('canvas')
    	);
    	return this._super.apply(this, arguments);
    },
    downloadable: true,
    printable: false,
});

_.each(['.wav', '.ogg', '.mp3', ], function(extension) {
	registry.add(extension, PreviewContentAudio);
});
_.each(['wav', 'ogg', 'mp3'], function(extension) {
	registry.add(extension, PreviewContentAudio);
});
_.each(['audio/wav', '	audio/ogg', 'audio/mpeg'], function(mimetype) {
	registry.add(mimetype, PreviewContentAudio);
});

return PreviewContentAudio;

});
