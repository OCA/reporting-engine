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

odoo.define('muk_web_utils.async', function (require) {
"use strict";

var core = require('web.core');

var _t = core._t;
var QWeb = core.qweb;

var syncLoop = function(items, func, callback) {
	items.reduce(function(promise, item) {
	    return promise.then(func.bind(this, item));
	}, $.Deferred().resolve()).then(callback);
};

var syncProgress = function(items, func, callback, update) {
	var progress = 0;
	items.reduce(function(promise, item) {
	    return promise.done(function() {
	    	update(++progress / items.length);
	    	return func(item);
	    });
	}, $.Deferred().resolve()).then(callback);
};

var createNotification = function(widget, title) {
	return widget.call('notification', 'notify', {
        title: title || _t('Upload'), 
        message: _t('Uploading...'),
        icon: 'fa-upload', 
        sticky: true,
        progress: {
        	text: "0%",
        	state: 0.0,
        },
    });
};

var updateNotification = function(widget, notification, progress) {
	widget.call('notification', 'progress', notification, {
    	text: (progress * 100).toFixed(2) + "%",
    	state: (progress * 100).toFixed(2),
    });
};

var closeNotification = function(widget, notification) {
	widget.call('notification', 'close', notification);
};

var syncNotification = function(widget, title, items, func, callback) {
	var notification = createNotification(widget, title);
	var update = _.partial(updateNotification, widget, notification);
	syncProgress(items, func, function() {
		$.when(closeNotification(widget, notification)).then(callback);
	}, update);
};

return {
	syncLoop: syncLoop,
	syncProgress: syncProgress,
	syncNotification: syncNotification,
};

});