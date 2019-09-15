/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Web Client 
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

odoo.define('muk_web_client.channel', function (require) {
"use strict";

var WebClient = require('web.WebClient');
var BusService = require('bus.BusService');

WebClient.include({
    init: function(parent, client_options){
    	this._super.apply(this, arguments);
        this.bus_channels = {};
    },
    bus_declare_channel: function(channel, method) {
    	if(!(channel in this.bus_channels)) {
    		this.bus_channels[channel] = method;
    		this.call('bus_service', 'addChannel', channel);
    	}
    },
    bus_delete_channel: function(channel) {
		this.call('bus_service', 'deleteChannel', channel);
        this.bus_channels = _.omit(this.bus_channels, channel);
    },
    show_application: function() {
        var res = this._super.apply(this, arguments);
        this.call('bus_service', 'onNotification', this, this.bus_notification);
        this.call('bus_service', 'startPolling');
        return res;
    },
    bus_notification: function(notifications) {
        _.each(notifications, function(notification, index) {
        	var channel = notification[0];
        	var message = notification[1];
        	if(channel in this.bus_channels) {
        		this.bus_channels[channel](message);
        	}
    	}, this);
    },
    destroy: function() {
    	_.each(this.bus_channels, function(method, channel) {
    		this.bus_delete_channel(channel);
    	}, this);
        this.call('bus_service', 'stopPolling');
        this._super.apply(this, arguments);
    },
});
    
});
