/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Web Notification 
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

odoo.define('muk_web_client_notification.channel', function (require) {
"use strict";

var WebClient = require('web.WebClient');
var NotificationService = require('web.NotificationService');

WebClient.include({
	show_application: function() {
        this.bus_declare_channel('notify', this.notify.bind(this));
        return this._super.apply(this, arguments);
    },
    notify: function(message) {
    	this.call('notification', 'notify', _.extend(message, {
    		buttons: _.map(message.buttons, function(button) {
    			button.click = this._notification_click.bind(this, {
    				'action': button.action, 
    				'options': button.options,
    				'button': button,
    				'message': message
    			});
    			return button;
    		}, this),
    	}));
    },
    _notification_click: function(params) {
    	this.action_manager.doAction(params.action, params.options)
    }
});
    
});