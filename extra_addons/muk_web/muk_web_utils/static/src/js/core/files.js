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

odoo.define('muk_web_utils.files', function (require) {
"use strict";

var core = require('web.core');

var QWeb = core.qweb;
var _t = core._t;

var traverseItems = function(items, tree) {
	var def = $.Deferred();
    var files = [];
    var defs = [];
    _.each(items, function(item, index) {
    	var entry = item.webkitGetAsEntry();
    	if(entry) {
    		var traverse = $.Deferred();
    		traverseEntry(entry, tree).then(function(result) {
    			if(tree) {
    				files = files.concat(result);
                } else {
                	files = _.union(files, result);
                }
    			traverse.resolve();
    		});
    		defs.push(traverse);
    	} else {
    		var file = item.getAsFile();
    		if(file) {
    			if(file.size) {
            		files.push(_.extend({}, file, {isFileItem: true}));
            	}
    		} else {
                console.warn("Your browser doesn't support Drag and Drop!");
            }
    	}
    });
    $.when.apply($, defs).then(function () {
        def.resolve(files);
    });
    return def;
};

var traverseEntries = function(entries, tree) {
	var def = $.Deferred();
    var files = [];
    var defs = [];
	_.each(entries, function(entry, index) {
		var traverse = $.Deferred();
		traverseEntry(entry, tree).then(function(result) {
			if(tree) {
				files = files.concat(result);
            } else {
            	files = _.union(files, result);
            }
			traverse.resolve();
		});
		defs.push(traverse);
    });
	$.when.apply($, defs).then(function () {
        def.resolve(files);
    });
    return def;
}

var traverseEntry = function(entry, tree) {
    var def = $.Deferred();
    if(entry.isFile) {
        def.resolve([entry]);
    } else if(entry.isDirectory) {
		entry.createReader().readEntries(function (entries) {
    		traverseEntries(entries, tree).then(function (files) {
                if(tree) {
                	def.resolve([{
                    	name: entry.name,
                    	files: files,
                    	isFile: false,
                    	isDirectory: true,
                    	childCount: files.length,
                    	fullPath: entry.fullPath,
                    	fileCount: _.reduce(files, function(sum, item) {
                    		return item.isFile ? sum + 1 : sum + item.fileCount || 0;
                    	}, 0),
                    }]);
                } else {
                	def.resolve(files);
                }
            });
        });
    } else {
    	def.resolve([]);
    }
    return def;
};

var getFileTree = function(items, count) {
	var traverse = traverseItems(items, true);
	if(count) {
	    var def = $.Deferred();
	    traverse.then(function(files) {
	    	def.resolve({
				files: files,
				count: _.reduce(files, function(sum, item) {
            		return item.isFile ? sum + 1 : sum + item.fileCount || 0;
            	}, 0),
			});
		});
		return def;
	}
	return traverse;
};

var getFileList = function(items, count) {
	var traverse = traverseItems(items, false);
	if(count) {
		var def = $.Deferred();
	    traverse.then(function(files) {
	    	def.resolve({
				files: files,
	    		count: files.length,
			});
			
		});
		return def;
	}
	return traverse;
};

var loadFile = function(file, callback) {
	var fileReader = new FileReader();
	fileReader.readAsDataURL(file);
	fileReader.onloadend = callback;
};

var readFile = function(file, callback) {
	if(file.isFile) {
		file.file(function(file) {
			loadFile(file, callback);
		});
	} else {
		loadFile(file, callback);
	}
};

return {
	traverseItems: traverseItems,
	traverseEntries: traverseEntries,
	traverseEntry: traverseEntry,
	getFileTree: getFileTree,
	getFileList: getFileList,
	loadFile: loadFile,
	readFile: readFile,
};

});
