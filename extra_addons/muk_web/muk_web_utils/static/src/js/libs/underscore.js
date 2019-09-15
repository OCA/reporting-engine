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

_.mixin({
	memoizeDebounce: function(func, wait, options) {
		wait = (typeof wait !== 'undefined') ? wait : 0;
		options = (typeof options !== 'undefined') ? options : {};
    	var mem = _.memoize(function() {
    		return _.debounce(func, wait, options)
    	}, options.resolver);
    	return function() {
    		mem.apply(this, arguments).apply(this, arguments)
    	}
    }
});

_.mixin({
    memoizeThrottle: function(func, wait, options) {
		wait = (typeof wait !== 'undefined') ? wait : 0;
		options = (typeof options !== 'undefined') ? options : {};
    	var mem = _.memoize(function() {
    		return _.throttle(func, wait, options)
    	}, options.resolver);
    	return function() {
    		mem.apply(this, arguments).apply(this, arguments)
    	}
    }
});