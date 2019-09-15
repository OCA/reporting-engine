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
odoo.define('muk_web_utils.tests.fields', function (require) {
"use strict";

var basicFields = require('web.basic_fields');
var concurrency = require('web.concurrency');
var config = require('web.config');
var core = require('web.core');
var FormView = require('web.FormView');
var KanbanView = require('web.KanbanView');
var ListView = require('web.ListView');
var session = require('web.session');
var testUtils = require('web.test_utils');
var field_registry = require('web.field_registry');

var createView = testUtils.createView;
var createAsyncView = testUtils.createAsyncView;
var DebouncedField = basicFields.DebouncedField;
var JournalDashboardGraph = basicFields.JournalDashboardGraph;
var _t = core._t;

QUnit.module('muk_web_utils', {}, function () {

QUnit.module('fields', {
    beforeEach: function () {
        this.data = {
            partner: {
                fields: {
                    display_name: {
                    	string: "Displayed name",
                    	type: "char",
                    	searchable: true
                    },
                    short: {
                    	string: "Short",
                    	type: "char",
                    	searchable: true,
                    	trim: true
                    },
                    long: {
                    	string: "Long",
                    	string: "txt",
                    	type: "text",
                    },
                    document: {
                    	string: "Binary", 
                    	type: "binary",
                    	attachment: true,
                    },
                },
                records: [{
                    id: 1,
                    display_name: "first record",
                    short: "Short Text",
                    long: "Super looooooong Text",
                    document: 'coucou==\n',
                }],
            },
        };
    }
}, function () {
	QUnit.module('BinaryFileCopy');

    QUnit.test('Fields is correctly rendered', function (assert) {
        assert.expect(2);

        var form = createView({
            View: FormView,
            model: 'partner',
            data: this.data,
            arch: (
            	'<form string="Partners">' +
                	'<field name="document" widget="copy_binary" filename="short"/>' +
                    '<field name="short"/>' +
            	'</form>'
            ),
            res_id: 1,
        });

        assert.strictEqual(
        	form.$('a.o_field_widget[name="document"] > .mk_copy_binary > .mk_copy_button').length, 
        	1, "the copy button should be visible in readonly mode"
        );

        form.$buttons.find('.o_form_button_edit').click();

        assert.strictEqual(
        	form.$('a.o_field_widget[name="document"] > .mk_copy_binary').length, 
        	0, "the copy button shouldn't be visible in edit mode"
        );
        
        form.destroy();
    });
    
    QUnit.module('CharShare');

    QUnit.test('Fields is correctly rendered', function (assert) {
        assert.expect(1);

        var form = createView({
            View: FormView,
            model: 'partner',
            data: this.data,
            arch: (
            	'<form string="Partners">' +
		        	'<div>' +
			            '<field name="short" widget="share_char"/>' +
		            '</div>' +
                '</form>'
            ),
            res_id: 1,
        });

        assert.strictEqual(
        	form.$('span.o_field_widget[name="short"] > .mk_share_dropdown.mk_share_char').length, 
        	1, "the copy button should be visible in readonly mode"
        );
        
        form.destroy();
    });
    
    QUnit.module('TextShare');

    QUnit.test('Fields is correctly rendered', function (assert) {
        assert.expect(1);

        var form = createView({
            View: FormView,
            model: 'partner',
            data: this.data,
            arch: (
            	'<form string="Partners">' +
		        	'<div>' +
			            '<field name="long" widget="share_text"/>' +
		            '</div>' +
                '</form>'
            ),
            res_id: 1,
        });

        assert.strictEqual(
        	form.$('span.o_field_widget[name="long"] > .mk_share_dropdown.mk_share_text').length, 
        	1, "the copy button should be visible in readonly mode"
        );
        
        form.destroy();
    });
    
    QUnit.module('BinaryFileShare');

    QUnit.test('Fields is correctly rendered', function (assert) {
        assert.expect(2);

        var form = createView({
            View: FormView,
            model: 'partner',
            data: this.data,
            arch: (
            	'<form string="Partners">' +
                	'<field name="document" widget="share_binary" filename="short"/>' +
                    '<field name="short"/>' +
            	'</form>'
            ),
            res_id: 1,
        });

        assert.strictEqual(
        	form.$('a.o_field_widget[name="document"] > .mk_share_dropdown > .mk_share_button').length, 
        	1, "the share dropdown should be visible in readonly mode"
        );

        form.$buttons.find('.o_form_button_edit').click();

        assert.strictEqual(
        	form.$('a.o_field_widget[name="document"] > .mk_share_dropdown > .mk_share_button').length, 
        	0, "the share dropdown shouldn't be visible in edit mode"
        );
        
        form.destroy();
    });
});

});

});