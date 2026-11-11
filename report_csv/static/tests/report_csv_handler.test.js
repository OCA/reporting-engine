import {
    defineActions,
    getService,
    mountWithCleanup,
    patchWithCleanup,
} from "@web/../tests/web_test_helpers";
import {expect, test} from "@odoo/hoot";
import {WebClient} from "@web/webclient/webclient";
import {download} from "@web/core/network/download";

defineActions([
    {
        id: 21,
        xml_id: "report_csv.partner_csv",
        name: "Print to CSV",
        report_name: "report_csv.partner_csv",
        report_type: "csv",
        type: "ir.actions.report",
        context: {active_ids: [1, 2]},
    },
]);

test("csv report actions download the csv and close once", async () => {
    patchWithCleanup(download, {
        _download: (options) => {
            const [url, type] = JSON.parse(options.data.data);
            expect.step(`${options.url} ${type} ${url.split("?")[0]}`);
            return Promise.resolve();
        },
    });
    await mountWithCleanup(WebClient);
    await getService("action").doAction(21, {
        onClose: () => expect.step("on_close"),
    });
    expect.verifySteps([
        "/report/download csv /report/csv/report_csv.partner_csv/1,2",
        "on_close",
    ]);
});
