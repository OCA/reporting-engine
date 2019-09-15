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

odoo.define('muk_web_utils.utils', function (require) {
"use strict";

var core = require('web.core');

var _t = core._t;
var QWeb = core.qweb;

var isUrl = function(string) {
	var protocol = string.match(/^(?:\w+:)?\/\/(\S+)$/);
	if (protocol && protocol[1]) {
		var localHost = (/^localhost[\:?\d]*(?:[^\:?\d]\S*)?$/).test(protocol[1]);
		var nonLocalHost = (/^localhost[\:?\d]*(?:[^\:?\d]\S*)?$/).test(protocol[1]);
		return !!(localHost || nonLocalHost);
	}
	return false;
}

var parseText2Html= function(text) {
    return text
        .replace(/((?:https?|ftp):\/\/[\S]+)/g,'<a href="$1">$1</a> ')
        .replace(/[\n\r]/g,'<br/>');
}

var closedRange = function(start, end) { 
	return _.range(start, end + 1);
}

var partitionPageList = function(pages, page, size) {
	if (!size || size < 5) {
		throw "The size must be at least 5 to partition the list.";
	}
	var sideSize = size < 9 ? 1 : 2;
	var leftSize = (size - sideSize * 2 - 3) >> 1;
	var rightSize = (size - sideSize * 2 - 2) >> 1;
	if (pages <= size) {
		return closedRange(1, pages);
	}
    if (page <= size - sideSize - 1 - rightSize) {
    	return closedRange(1, size - sideSize - 1)
    		.concat([false])
    		.concat(closedRange(pages - sideSize + 1, pages));
    }
    if (page >= pages - sideSize - 1 - rightSize) {
    	return closedRange(1, sideSize)
    		.concat([false])
    		.concat(closedRange(pages - sideSize - 1 - rightSize - leftSize, pages));
    }
    return closedRange(1, sideSize)
	    .concat([false])
	    .concat(closedRange(page - leftSize, page + rightSize))
	    .concat([false])
	    .concat(closedRange(pages - sideSize + 1, pages));
}

return {
	isUrl: isUrl,
	closedRange: closedRange,
	parseText2Html: parseText2Html,
	partitionPageList: partitionPageList,
};

});