// © 2017 Creu Blanca
// License AGPL-3.0 or later (https://www.gnuorg/licenses/agpl.html).
odoo.define("report_qweb_encrypt.Dialog", function (require) {
    "use strict";

    var ActionManager = require("web.ActionManager");
    var Dialog = require("web.Dialog");
    var core = require("web.core");

    var _t = core._t;

    var EncryptDialog = Dialog.extend({
        events: _.extend({}, Dialog.prototype.events, {
            change: "_onChange",
        }),
        _setValue: function () {
            this.value = this.$el.find(".o_password").val();
        },
        _onChange: function () {
            this._setValue();
        },
    });
    EncryptDialog.askPassword = function (owner, action, action_options, options) {
        var buttons = [
            {
                text: _t("Ok"),
                classes: "btn-primary",
                close: true,
                click: function () {
                    var password = this.value || false;
                    owner._executeReportAction(action, action_options, password);
                },
            },
            {
                text: _t("Cancel"),
                close: true,
                click: false,
            },
        ];
        return new EncryptDialog(
            owner,
            _.extend(
                {
                    size: "small",
                    buttons: buttons,
                    $content: $(
                        '<div><input class="o_password" type="password"/></div>'
                    ),
                    title: _t("Encrypt"),
                },
                options
            )
        ).open();
    };

    ActionManager.include({
        _executeReportAction: function (action, options, password) {
            if (
                action.encrypt === "manual" &&
                action.report_type === "qweb-pdf" &&
                password === undefined
            ) {
                EncryptDialog.askPassword(this, action, options);
                return $.Deferred();
            } else if (action.encrypt === "manual") {
                action.context = _.extend({}, action.context, {
                    encrypt_password: password,
                });
            }
            return this._super(action, options, password);
        },
        _makeReportUrls: function (action) {
            var reportUrls = this._super.apply(this, arguments);
            if (action.encrypt === "manual" && action.context.encrypt_password) {
                if (
                    _.isUndefined(action.data) ||
                    _.isNull(action.data) ||
                    (_.isObject(action.data) && _.isEmpty(action.data))
                ) {
                    var serializedOptionsPath =
                        "?context=" +
                        encodeURIComponent(
                            JSON.stringify({
                                encrypt_password: action.context.encrypt_password,
                            })
                        );
                    reportUrls = _.mapObject(reportUrls, function (value) {
                        value += serializedOptionsPath;
                        return value;
                    });
                }
            }
            return reportUrls;
        },
    });
});
