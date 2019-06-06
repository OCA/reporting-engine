/* Copyright 2015-2019 Onestein (<https://www.onestein.eu>)
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl). */

odoo.define('bi_view_editor.JoinNodeDialog', function (require) {
    "use strict";

    var Dialog = require("web.Dialog");
    var core = require('web.core');
    var qweb = core.qweb;
    var _t = core._t;

    var JoinNodeDialog = Dialog.extend({
        xmlDependencies: Dialog.prototype.xmlDependencies.concat([
            '/bi_view_editor/static/src/xml/bi_view_editor.xml',
        ]),
        events: {
            "click li": "choiceClicked",
        },
        init: function (parent, options, choices, model_data) {
            this.choices = choices;
            // Prepare data for view
            for (var i = 0; i < choices.length; i++) {
                if (choices[i].join_node !== -1 && choices[i].table_alias !== -1) {
                    choices[i].model_name = model_data[choices[i].table_alias].model_name;
                }
                choices[i].index = i;
            }

            var defaults = _.defaults(options || {}, {
                title: _t("Join..."),
                dialogClass: 'oe_act_window',
                $content: qweb.render('bi_view_editor.JoinNodeDialog', {
                    'choices': choices,
                }),
                buttons: [{
                    text: _t("Cancel"),
                    classes: "btn-default o_form_button_cancel",
                    close: true,
                }],
            });
            this._super(parent, defaults);
        },
        choiceClicked: function (e) {
            this.trigger('chosen', {
                choice: this.choices[$(e.currentTarget).attr('data-index')],
            });
            this.close();
        },
    });

    return JoinNodeDialog;
});
