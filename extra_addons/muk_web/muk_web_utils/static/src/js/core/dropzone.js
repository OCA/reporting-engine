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

odoo.define('muk_web_utils.dropzone', function (require) {
"use strict";

var core = require('web.core');

var _t = core._t;
var QWeb = core.qweb;

var DropzoneMixin = {
	dropzoneData: {},
	dropzoneClasses: ['mk_dropzone'],
	_checkDropzoneEvent: function(event) {
		return true;
	},
	_startDropzone: function($dropzone) {
		if(this.$dropzone) {
			this._destroyDropzone();
		}
		this.$dropzone = $dropzone;
		this.$dropzone.dndHover().on({
            'dndHoverStart.dropzone': this._hoverDropzoneEnter.bind(this),
            'dndHoverEnd.dropzone': this._hoverDropzoneLeave.bind(this),
        });
		this.$dropzone.on('dragenter.dropzone', this._dragenterDropzone.bind(this));
		this.$dropzone.on('dragover.dropzone', this._dragoverDropzone.bind(this));
		this.$dropzone.on('dragleave.dropzone', this._dragleaveDropzone.bind(this));
		this.$dropzone.on('drop.dropzone', this._dropDropzone.bind(this));
		_.each(this.dropzoneData, function(value, key) {
			this.$dropzone.attr(key, value)
		}, this);
	},
	_destroyDropzone: function() {
		if(this.$dropzone) {
			this.$dropzone.off('.dropzone');
			this.$dropzone.dndHover('destroy');
			_.each(this.dropzoneData, function(value, key) {
				this.$dropzone.removeAttr(key)
			}, this);
			this.$dropzone = false;
		}
	},
	_toggleDropzone: function(state) {
		this.$dropzone.toggleClass(this.dropzoneClasses.join(" "), state);
	},
	_hoverDropzoneEnter: function(event, originalEvent) {
		if(this._checkDropzoneEvent(originalEvent)) {
	    	this._toggleDropzone(true);
	    	event.preventDefault();
			return false;
    	}
	},
	_hoverDropzoneLeave: function(event, originalEvent) {
    	this._toggleDropzone(false);
    	event.stopPropagation();
    	event.preventDefault();
        return false;
	},
	_handleDrag: function(event) {
	},
	_handleDrop: function(event) {
	},
	_dragenterDropzone: function(event) {
    	if(this._checkDropzoneEvent(event)) {
	    	event.preventDefault();
    	}
    },
    _dragoverDropzone: function(event) {
    	if(this._checkDropzoneEvent(event)) {
        	event.preventDefault();
    		this._handleDrag(event);
    	}
    },
    _dragleaveDropzone: function(event) {
    	if(this._checkDropzoneEvent(event)) {
	    	event.preventDefault();
    	}
    },
    _dropDropzone: function(event) {
    	if(this._checkDropzoneEvent(event)) {
        	event.preventDefault();
//    		event.stopPropagation();
    		this._handleDrop(event);
    	}
    }
};

var FileDropzoneMixin = _.extend({}, DropzoneMixin, {
	dropzoneData: {
		'data-dropzone-text': _t("Drop files here to upload!"),
	},
	dropzoneClasses: DropzoneMixin.dropzoneClasses.concat(['mk_dropzone_file']),
	dropzoneCheck: window.File && window.FileReader && window.FileList && window.Blob,
	_checkDropzoneEvent: function(event) {
		var dataTransfer = event.originalEvent && event.originalEvent.dataTransfer;
		var fileCheck = dataTransfer && _.some(dataTransfer.types, function(type) {
			return type == "Files";
		});
		return this.dropzoneCheck && fileCheck;
	},
	_handleDrag: function(event) {
		event.originalEvent.dataTransfer.dropEffect = 'copy';
	},
});

return {
	DropzoneMixin: DropzoneMixin,
	FileDropzoneMixin: FileDropzoneMixin,
};

});