odoo.define("report_async.action_menus_tests", function (require) {
    "use strict";
    /* global QUnit*/

    const ActionMenus = require("web.ActionMenus");
    const Registry = require("web.Registry");
    const testUtils = require("web.test_utils");
    const cpHelpers = testUtils.controlPanel;

    const {createComponent} = testUtils;

    QUnit.module(
        "report_async",
        {
            beforeEach() {
                this.action = {
                    res_model: "res.users",
                };
                this.view = {
                    type: "form",
                };
                this.props = {
                    activeIds: [1, 2],
                    context: {},
                    items: {
                        print: [
                            {
                                type: "ir.actions.report",
                                async_report: true,
                                data: null,
                                async_no_records: 1,
                                async_mail_recipient: "admin@example.com",
                                report_type: "qweb-pdf",
                                report_name: "report_async.async_demo_report_view",
                                report_file: "report_async.async_demo_report_view",
                                name: "Async Report",
                                id: 1,
                            },
                        ],
                    },
                };
                // Patch the registry of the action menus
                this.actionMenusRegistry = ActionMenus.registry;
                ActionMenus.registry = new Registry();
            },
            afterEach() {
                ActionMenus.registry = this.actionMenusRegistry;
            },
        },
        function () {
            QUnit.test("execute print action", async function (assert) {
                // No of assertion expected.
                assert.expect(7);
                const actionMenus = await createComponent(ActionMenus, {
                    env: {
                        action: this.action,
                        view: this.view,
                    },
                    intercepts: {
                        "do-action": () => assert.step("do-action"),
                    },
                    props: this.props,
                    async mockRPC(route, args) {
                        switch (route) {
                            case "/web/action/load": {
                                const expectedContext = {
                                    active_id: 1,
                                    active_ids: [1, 2],
                                    active_model: "res.users",
                                };
                                assert.deepEqual(args.context, expectedContext);
                                assert.step("load-action");
                                return {context: {}, flags: {}};
                            }
                            default:
                                return this._super(...arguments);
                        }
                    },
                });
                await testUtils.nextTick();
                await cpHelpers.toggleActionMenu(actionMenus, "Print");
                await cpHelpers.toggleMenuItem(actionMenus, "Async Report");

                // We should have dialog created and opened
                assert.containsOnce(
                    $,
                    ".form",
                    "Error dialog should be opened and showing async options"
                );
                // We should have checkbox checked
                assert.ok(
                    $("#async_report_checker").prop("checked"),
                    "Checkbox should be checked auto"
                );

                // Email should be set as default
                assert.equal(
                    $("#async-user-email").val(),
                    "admin@example.com",
                    "Email should be set and equal to default"
                );

                // Try to process async report to a queue and send mail
                await testUtils.dom.click($("button.btn-primary"), {
                    allowInvisible: true,
                });
                await testUtils.nextTick();

                // This should fail through error/alert dialog because we haven't
                // defined the report well queue job, qweb etc. For a successful
                // test see possible python tests.
                assert.containsNone(
                    $,
                    $(".modal-content"),
                    "Error Dialog should have popup"
                );
                assert.ok(
                    $(".modal-title").text(),
                    "Report",
                    'Should have title "Report"'
                );
                assert.ok($(".modal-content").text().search("Failed"));

                // Close error dialog
                await testUtils.dom.click($(".modal-footer button.btn-primary"), {
                    allowInvisible: true,
                });
                await testUtils.nextTick();

                // All dialogs should be closed
                assert.containsNone($, $(".modal-dialog"), "Dialogs should be closed");

                // Destroy the action menus
                actionMenus.destroy();
            });
        }
    );
});
