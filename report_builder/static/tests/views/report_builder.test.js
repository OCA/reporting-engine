import {animationFrame, expect, test} from "@odoo/hoot";
import {defineModels, fields, models, mountView} from "@web/../tests/web_test_helpers";
import {defineMailModels} from "@mail/../tests/mail_test_helpers";

class ReportInstance extends models.Model {
    _name = "report.instance";

    name = fields.Char();
    data = fields.Json();
    currency_id = fields.Many2one({relation: "res.currency"});
    show_search_bar = fields.Boolean();
    search_view_id = fields.Many2one({relation: "ir.ui.view"});
    search_res_model = fields.Char();
    show_settings = fields.Boolean();
    show_pivot_date = fields.Boolean();

    process_information() {
        return {
            2: {
                4: {total: 1},
                5: {total: 2},
            },
            3: {
                4: {total: 3},
                5: {total: 4},
            },
        };
    }

    _views = {
        form: `
            <form>
                <sheet>
                    <field name="id" widget="report_builder" />
                </sheet>
            </form>
            `,
    };
    _records = [
        {
            id: 1,
            name: "Report 1",
            currency_id: 1,
            data: {
                date: "2024-01-01",
                rows: [
                    {
                        id: 2,
                        name: "Row 1",
                    },
                    {
                        id: 3,
                        name: "Row 2",
                    },
                ],
                columns: [
                    {id: 4, name: "Column 1"},
                    {id: 5, name: "Column 2"},
                ],
            },
        },
    ];
}
defineModels([ReportInstance]);
// As we use mail as a dependancy, we need to declare models.
defineMailModels();

test("Check selected item", async () => {
    await mountView({
        type: "form",
        resId: 1,
        resIds: [1],
        resModel: "report.instance",
    });
    await animationFrame();
    expect(".o_report_builder_value").toHaveCount(4);
    expect('.o_report_builder_value:contains("$ 1.00")').toHaveCount(1);
    expect('.o_report_builder_value:contains("$ 2.00")').toHaveCount(1);
    expect('.o_report_builder_value:contains("$ 3.00")').toHaveCount(1);
    expect('.o_report_builder_value:contains("$ 4.00")').toHaveCount(1);
});
