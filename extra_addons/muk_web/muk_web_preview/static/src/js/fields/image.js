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

odoo.define('muk_web_preview.image', function (require) {
"use strict";

var core = require('web.core');
var utils = require('web.utils');
var session = require('web.session');
var fields = require('web.basic_fields');
var field_utils = require('web.field_utils');

var PreviewManager = require('muk_preview.PreviewManager');
var PreviewDialog = require('muk_preview.PreviewDialog');

var _t = core._t;
var QWeb = core.qweb;

fields.FieldBinaryImage.include({
	events: _.extend({}, fields.FieldBinaryImage.prototype.events, {
        'click img': 'onImagePreview',
    }),
    _render: function () {
    	this._super.apply(this, arguments);
    	if (this.nodeOptions.no_preview) {
    		this.$('.mk_field_image_wrapper').addClass('mk_no_preview');
    	}
    },
    onImagePreview: function () {
        if (this.mode === "readonly" && !this.nodeOptions.no_preview) {
            var last_update =  this.recordData.__last_update;
            var unique = last_update && field_utils.format.datetime(last_update);
            var binary_url = session.url('/web/content', {
                model: this.model,
                id: JSON.stringify(this.res_id),
                data: utils.is_bin_size(this.value) ? null : this.value,
                unique: unique ? unique.replace(/[^0-9]/g, '') : null,
                field: this.name,
                download: true,
            });
            var preview = new PreviewDialog(
        		this, [{
        			url: binary_url,
        			filename: "image.png",
        			mimetype: "image/png",
        		}], 0
            );
            preview.appendTo($('body'));
        	event.stopPropagation();
        	event.preventDefault();
        }
    },
});

});
