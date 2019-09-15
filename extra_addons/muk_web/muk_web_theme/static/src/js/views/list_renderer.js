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

odoo.define('muk_web_theme.ListRenderer', function (require) {
"use strict";

var dom = require('web.dom');
var core = require('web.core');
var config = require("web.config");

var ListRenderer = require('web.ListRenderer');

var _t = core._t;
var QWeb = core.qweb;

ListRenderer.include({
    _range_history: [],
    _render: function() {
        var res = this._super.apply(this, arguments);
        this.$table = this.$el.find('.o_list_view');
        return res;
    },
    _getRangeSelection: function() {
        var self = this;
        var start = null, end = null;
        this.$el.find('td.o_list_record_selector input').each(function (i, el) {
            var id = $(el).closest('tr').data('id');
            var checked = self._range_history.indexOf(id) !== -1;
            if (checked && $(el).is(':checked')) {
                if (start == null) {
                    start = i;
                } else {
                    end = i;
                }
            }
        });
        var new_range = this._getSelectionByRange(start, end);
        var current_selection = this.selection;
        current_selection = _.uniq(current_selection.concat(new_range));
        return current_selection;
    },
    _getSelectionByRange: function(start, end) {
        var result = [];
        this.$el.find('td.o_list_record_selector input').closest('tr').each(function (i, el) {
            var record_id = $(el).data('id');
            if (start != null && end != null && i >= start && i <= end) {
                result.push(record_id);
            } else if(start != null && end == null && start == i) {
                result.push(record_id);
            }
        });
        return result;
    },
    _pushRangeHistory: function(id) {
        if (this._range_history.length === 2) {
            this._range_history = [];
        }
        this._range_history.push(id);
    },
    _deselectTable: function() {
        window.getSelection().removeAllRanges();
    },
    _onSelectRecord: function(event) {
        var res = this._super.apply(this, arguments);
        var element = $(event.currentTarget);
        if (/firefox/i.test(navigator.userAgent) && event.shiftKey) {
            element.find('input').prop('checked', !element.find('input').prop('checked'));
        }
        if (element.find('input').prop('checked')) {
            this._pushRangeHistory(element.closest('tr').data('id'));
        }
        if (event.shiftKey) {
            var selection = this._getRangeSelection();
            var $rows = this.$el.find('td.o_list_record_selector input').closest('tr');
            $rows.each(function () {
                var record_id = $(this).data('id');
                if (selection.indexOf(record_id) !== -1) {
                    $(this).find('td.o_list_record_selector input').prop('checked', true);
                }
            });
            this._updateSelection();
            this._deselectTable();
        }
        return res;
    }
});

});