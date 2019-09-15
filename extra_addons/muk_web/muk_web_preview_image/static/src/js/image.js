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

odoo.define('muk_preview_markdown.PreviewContentImage', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentImage = AbstractPreviewContent.extend({
	template: "muk_preview.PreviewContentImage",    
	cssLibs: [
    ],
    jsLibs: [
    ],
    renderPreviewContent: function() {
    	this.$('.mk_preview_image').css({
            "background-size": "contain",
            "background-repeat": "no-repeat",
            "background-position": "center",
            "background-image": "url(" + this.url + ")"
        });
    },
    downloadable: true,
    printable: true,
});

_.each([
	'cod', 'ras', 'fif', 'gif', 'ief', 'jpeg', 'jpg', 'jpe', 'png', 'tiff',
    'tif', 'mcf', 'wbmp', 'fh4', 'fh5', 'fhc', 'ico', 'pnm', 'pbm', 'pgm',
    'ppm', 'rgb', 'xwd', 'xbm', 'xpm'
], function(extension) {
	registry.add(extension, PreviewContentImage);
	registry.add("." + extension, PreviewContentImage);
});
_.each([
	'image/cis-cod', 'image/cmu-raster', 'image/fif', 'image/gif', 'image/ief',
	'image/png', 'image/tiff', 'image/vasa', 'image/vnd.wap.wbmp', 'image/x-freehand',
	'image/x-portable-anymap', 'image/x-portable-bitmap', 'image/x-portable-graymap',
	'image/x-portable-pixmap', 'image/x-rgb', 'image/x-windowdump', 'image/x-xbitmap', 
	'image/jpeg', 'image/x-icon', 'image/x-xpixmap'
], function(mimetype) {
	registry.add(mimetype, PreviewContentImage);
});

return PreviewContentImage;

});
