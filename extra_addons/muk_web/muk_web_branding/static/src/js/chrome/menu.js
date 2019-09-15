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

odoo.define('muk_web_branding.menu', function (require) {
"use strict";

var core = require('web.core');
var session = require('web.session');

var UserMenu = require('web.UserMenu');

var _t = core._t;
var QWeb = core.qweb;

UserMenu.include({
    start: function () {
    	if (!session.is_admin) {
            this.$('.mk_debug_divider').remove();
            this.$('a[data-menu="debug"]').remove();
            this.$('a[data-menu="debugassets"]').remove();
    	}
        return this._super.apply(this, arguments)
    },
    _onMenuDocumentation: function () {
        window.open(session.muk_branding_documentation + '/documentation', '_blank');
    },
    _onMenuSupport: function () {
        window.open(session.muk_branding_support, '_blank');
    },
    _onMenuDebug: function(){
        if (session.debug && session.debug !== 'assets'){
            return console.log(_t('Developer mode is already activated'));
        }
        window.location = $.param.querystring(window.location.href, 'debug');
    },
    _onMenuDebugassets: function(){
        if (session.debug === 'assets'){
            return console.log(_t('Developer mode is already activated'));
        }
        window.location = $.param.querystring(window.location.href, 'debug=assets');
    }
});

});