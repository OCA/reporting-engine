/**********************************************************************************
*
*    Copyright (c) 2017-2019 MuK IT GmbH.
*
*    This file is part of MuK Preview Text 
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

odoo.define('muk_preview_markdown.PreviewContentText', function (require) {
"use strict";

var core = require('web.core');
var ajax = require('web.ajax');
var utils = require('web.utils');
var session = require('web.session');

var registry = require('muk_preview.registry');

var AbstractPreviewContent = require('muk_preview.AbstractPreviewContent');

var QWeb = core.qweb;
var _t = core._t;

var PreviewContentText = AbstractPreviewContent.extend({
	events: _.extend({}, AbstractPreviewContent.prototype.events, {
		'change .code-lang': '_onLanguageChange',
	}),
	template: "muk_preview.PreviewContentText",    
	cssLibs: [
		'/muk_web_preview_text/static/lib/highlight/styles/default.css',
    ],
    jsLibs: [
        '/muk_web_preview_text/static/lib/highlight/highlight.pack.js',
        '/muk_web_preview_text/static/lib/highlight_line_numbers/highlight_line_numbers.js',
    ],
	willStart: function() { 
		var def = $.ajax({
		  url: this.url,
		  dataType: "text",
		}).fail(function(jqXHR, textStatus) {
			console.error(textStatus);
		}).done(function(text) {
			this.text = text;
		}.bind(this));
		return $.when(this._super.apply(this, arguments), def);
    },
    renderPreviewContent: function() {
    	this.$codeBlock = this.$('.code-view');
    	this.$codeLang = this.$('.code-lang');
    	this._setTextLanguage();
    	this.$codeLang.select2();
    	$.each(this.$codeBlock.attr('class').split(" "), function (i, cls) {
    	    if(this.$(".code-lang option[value='" + cls + "']").val()) {
    	    	this.$codeLang.val(cls).trigger("change");
    	    }
    	}.bind(this));
    	return this._super.apply(this, arguments);
    },
    _onLanguageChange: function(event) {
    	if(event.val === 'default') {
    		this._setTextLanguage();
		} else {
			this._setTextLanguage(event.val);
		}
    },
    _setTextLanguage: function (language) {
		this.$codeBlock.removeClass();
		this.$codeBlock.addClass('code-view');
		if(language) {
			this.$codeBlock.addClass(language);
		}
		this.$codeBlock.text(this.text);
		hljs.highlightBlock(this.$codeBlock[0]);
	    hljs.lineNumbersBlock(this.$codeBlock[0]);
	},
    downloadable: true,
    printable: true,
});

_.each([
	'abc', 'acgi', 'aip', 'asm', 'asp', 'c', 'c', 'c++', 'cc', 'cc', 'com', 'conf',
	'cpp', 'csh', 'css', 'cxx', 'def', 'el', 'etx', 'f', 'f', 'f77', 'f90', 'f90',
	'flx', 'for', 'for', 'g', 'h', 'h', 'hh', 'hh', 'hlb', 'htc', 'htm', 'html',
	'htmls', 'htt', 'htx', 'idc', 'jav', 'jav', 'java', 'java', 'js', 'js', 'ksh',
	'list', 'log', 'lsp', 'lst', 'lsx', 'm', 'm', 'mar', 'mcf', 'p', 'pas', 'pl',
	'pl', 'pm', 'py', 'rexx', 'rt', 'rt', 'rtf', 'rtx', 's', 'scm', 'scm', 'sdml',
	'sgm', 'sgm', 'sgml', 'sgml', 'sh', 'shtml', 'shtml', 'spc', 'ssi', 'talk', 'tcl',
	'tcsh', 'text', 'tsv', 'txt', 'uil', 'uni', 'unis', 'uri', 'uris', 'uu', 'uue',
	'vcs', 'wml', 'wmls', 'wsc', 'xml', 'zsh', 'less', 'aj', 'cbl', 'cs', 'coffee',
	'go', 'groovy', 'sc', 'js', 'json',
], function(extension) {
	registry.add(extension, PreviewContentText);
	registry.add("." + extension, PreviewContentText);
});
_.each([
	'text/vnd.abc', 'text/html', 'text/x-audiosoft-intra', 'text/x-asm', 'text/asp', 'text/plain',
	'text/x-c', 'text/x-script.csh', 'text/css', 'text/x-script.elisp', 'text/x-setext', 'text/x-fortran',
	'text/vnd.fmi.flexstor', 'text/x-h', 'text/x-script', 'text/x-component', 'text/webviewhtml',
	'text/x-java-source', 'text/javascript', 'text/ecmascript', 'text/x-script.ksh', 'text/x-script.lisp',
	'text/x-la-asf', 'text/x-m', 'text/mcf', 'text/x-pascal', 'text/pascal', 'text/x-script.perl',
	'text/x-script.perl-module', 'text/x-script.phyton', 'text/x-script.rexx', 'text/richtext',
	'text/vnd.rn-realtext', 'text/x-script.guile', 'text/x-script.scheme', 'text/sgml', 'text/x-sgml',
	'text/x-script.sh', 'text/x-server-parsed-html', 'text/x-speech', 'text/x-script.tcl',
	'text/x-script.tcsh', 'text/tab-separated-values', 'text/x-uil', 'text/uri-list', 'text/x-uuencode',
	'text/x-vcalendar', 'text/vnd.wap.wml', 'text/vnd.wap.wmlscript', 'text/scriplet', 'text/xml',
	'text/x-script.zsh', 'text/javascript', 'application/javascript', 'application/json', 
], function(mimetype) {
	registry.add(mimetype, PreviewContentText);
});

return PreviewContentText;

});
