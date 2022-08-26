odoo.define("report_async.ActionMenus", function (require) {
    "use strict";

    const {patch} = require("web.utils");
    const ActionMenus = require("web.ActionMenus");
    const Dialog = require("web.Dialog");
    const Core = require("web.core");
    const Framework = require("web.framework");

    const _t = Core._t;
    const QWeb = Core.qweb;

    function validate_email(email) {
        const res = email.match(
            /^(([^<>()[\]\\.,;:\s@"]+(\.[^<>()[\]\\.,;:\s@"]+)*)|(".+"))@((\[[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\])|(([a-zA-Z\-0-9]+\.)+[a-zA-Z]{2,}))$/
        );
        if (!res) {
            return false;
        }
        return true;
    }

    // Patch _executeAction to use Dialog
    patch(ActionMenus, "async _super report_async.ActionMenus", {
        async _executeAction(action) {
            const self = this;
            const _super = this._super;
            const args = arguments;
            const records = this.props.activeIds;
            var $content = $(QWeb.render("ReportAsyncConfiguration", {}));

            if (action.async_report && records.length >= action.async_no_records) {
                const asyncDialog = new Dialog(self, {
                    title:
                        _t("Async Report Configuration ") +
                        "(" +
                        action.display_name +
                        ")",
                    size: "medium",
                    buttons: [
                        {
                            text: _t("Print"),
                            classes: "btn-primary",
                            close: true,
                            click: function () {
                                const is_report_async = this.$(
                                    "#async_report_checker"
                                ).prop("checked");
                                const save_report_attachment = this.$(
                                    "#async-save-report-checker"
                                ).prop("checked");
                                const user_email = this.$("#async-user-email").val();
                                if (user_email !== "" && is_report_async) {
                                    // Try basic email validation
                                    if (validate_email(user_email)) {
                                        if (
                                            "report_type" in action &&
                                            action.report_type === "qweb-pdf"
                                        ) {
                                            Framework.unblockUI();
                                            // Generate report async
                                            self.rpc({
                                                model: "report.async",
                                                method: "print_document_async",
                                                args: [records, action.report_name],
                                                kwargs: {
                                                    to_email: user_email,
                                                    data: action.data || {},
                                                    context: action.context || {},
                                                    save_attachment_to_records: save_report_attachment,
                                                },
                                            })
                                                .then(() => {
                                                    const msg =
                                                        _t(
                                                            "Job started to generate report. Upon " +
                                                                "completion, mail sent to:"
                                                        ) + user_email;
                                                    Dialog.alert(self, msg, {
                                                        title: _t("Report"),
                                                    });
                                                })
                                                .catch(() => {
                                                    const error = _t(
                                                        "Failed, error on job creation."
                                                    );
                                                    const title = _t("Report");
                                                    Dialog.alert(self, error, {
                                                        title: title,
                                                    });
                                                });
                                        } else {
                                            // Default to normal approach to generate report
                                            return _super.apply(self, args);
                                        }
                                    } else {
                                        const msg = _t(
                                            "Please check your email syntax and try again"
                                        );
                                        const title = _t("Email Validation Error");
                                        Dialog.alert(self, msg, {title: title});
                                    }
                                } else {
                                    // Default to normal approach to generate report
                                    return _super.apply(self, args);
                                }
                            },
                        },
                        {
                            text: _t("Discard"),
                            close: true,
                        },
                    ],
                    $content: $content,
                });
                // Default current user mail
                asyncDialog.open().opened(function () {
                    asyncDialog.$el
                        .find("#async-user-email")
                        .val(action.async_mail_recipient);
                });
            } else {
                // Default to normal approach to generate report
                return _super.apply(this, arguments);
            }
        },
    });
});
