/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview Video 
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

odoo.define('muk_preview_markdown.PreviewContentVideo', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentVideo = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentVideo",    
    mimetypeMap: {
		'.mp4': 'video/mp4', '.webm': 'video/webm', '.ogg': 'video/ogg',
		'mp4': 'video/mp4', 'webm': 'video/webm', 'ogg': 'video/ogg',
	},
	init: function(parent, url, mimetype, filename) {
    	this._super.apply(this, arguments);
    	if(this.mimetype === 'application/octet-stream') {
    		var extension = this.filename.split('.').pop();
    		this.mimetype = this.mimetypeMap[extension];
    	}
    },
    downloadable: true,
    printable: false,
});

_.each(['.mp4', '.webm', '.ogg'], function(extension) {
	registry.add(extension, PreviewContentVideo);
});
_.each(['mp4', 'webm', 'ogg'], function(extension) {
	registry.add(extension, PreviewContentVideo);
});
_.each(['video/mp4', '	video/webm', 'video/ogg'], function(mimetype) {
	registry.add(mimetype, PreviewContentVideo);
});

return PreviewContentVideo;

});
