/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Web Branding 
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

odoo.define('muk_web_branding.dashboard', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var dashboard = require('web_settings_dashboard');

var _t = core._t;
var QWeb = core.qweb;

dashboard.DashboardApps.include({
    start: function() {
    	this._super.apply(this, arguments);
    	var $store = $('<a/>', {
    		target: "_blank",
    		href: this.data.store,
    		html: '<i class="fa fa-lg fa-rocket text-muted"></i> App store',
    		class: "flex-grow-1 w-25",
    	});
    	this.$('.o_web_settings_dashboard_pills').html($store);
    	this.$('.o_web_settings_dashboard_enterprise').remove();
    },
});

dashboard.DashboardShare.include({
	init: function (parent, data) {
		this._super.apply(this, arguments);
        this.share_url = this.data.share;
        this.share_text = encodeURIComponent(_.str.sprintf(
    		_t("I am using #%s - Awesome open source business apps."),
    		this.data.system
    	));
        this.share_description = _.str.sprintf(
    		_t("Mantained by %s"), this.data.publisher
    	);
    },
    start: function() {
        this._super.apply(this, arguments);
        this.$('.o_web_settings_dashboard_compact_subtitle > small').text(this.share_description);
    },
});

});