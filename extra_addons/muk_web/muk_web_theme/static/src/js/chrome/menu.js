/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Backend Theme 
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

odoo.define('muk_web_theme.Menu', function (require) {
"use strict";

var core = require('web.core');
var config = require("web.config");

var Menu = require("web.Menu");
var AppsBar = require("muk_web_theme.AppsBar");

var _t = core._t;
var QWeb = core.qweb;

Menu.include({
    events: _.extend({}, Menu.prototype.events, {
    	"click .o_menu_apps a[data-toggle=dropdown]": "_onAppsMenuClick",
    	"click .mk_menu_mobile_section": "_onMobileSectionClick",
        "click .o_menu_sections [role=menuitem]": "_hideMobileSubmenus",
        "show.bs.dropdown .o_menu_systray, .o_menu_apps": "_hideMobileSubmenus",
    }),
    menusTemplate: config.device.isMobile ? 
    		'muk_web_theme.MobileMenu.sections' : Menu.prototype.menusTemplate,
    start: function () {
    	var res = this._super.apply(this, arguments);
        this.$menu_toggle = this.$(".mk_menu_sections_toggle");
        this.$menu_apps_sidebar = this.$('.mk_apps_sidebar_panel');
        this._appsBar = new AppsBar(this, this.menu_data);
        this._appsBar.appendTo(this.$menu_apps_sidebar);
        this.$menu_apps_sidebar.renderScrollBar();
        if (config.device.isMobile) {
            var menu_ids = _.keys(this.$menu_sections);
            for (var i = 0; i < menu_ids.length; i++) {
            	var $section = this.$menu_sections[menu_ids[i]];
            	$section.on('click', 'a[data-menu]', this, function(ev) {
                	ev.stopPropagation();
                });
            }
        } 
        return res;
    },
    _hideMobileSubmenus: function () {
        if (this.$menu_toggle.is(":visible") && $('.oe_wait').length === 0 && 
        		this.$section_placeholder.is(":visible")) {
            this.$section_placeholder.collapse("hide");
        }
    },
    _updateMenuBrand: function () {
        if (!config.device.isMobile) {
            return this._super.apply(this, arguments);
        }
    },
    _onAppsMenuClick: function(event, checkedCanBeRemoved) {
    	var action_manager = this.getParent().action_manager;
    	var controller = action_manager.getCurrentController();
    	if (controller && !checkedCanBeRemoved) {
    		controller.widget.canBeRemoved().done(function () {
    			$(event.currentTarget).trigger('click', [true]);
    			$(event.currentTarget).off('.bs.dropdown');
            });
        	event.stopPropagation();
        	event.preventDefault();
        }
    },
    _onMobileSectionClick: function (event) {
    	event.preventDefault();
    	event.stopPropagation();
    	var $section = $(event.currentTarget);
    	if ($section.hasClass('show')) {
    		$section.removeClass('show');
    		$section.find('.show').removeClass('show');
    		$section.find('.fa-chevron-down').hide();
    		$section.find('.fa-chevron-right').show();
    	} else {
    		$section.addClass('show');
    		$section.find('ul:first').addClass('show');
    		$section.find('.fa-chevron-down:first').show();
    		$section.find('.fa-chevron-right:first').hide();
    	}
    },
});

});