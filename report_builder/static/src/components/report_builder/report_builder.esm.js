import {Component, onWillStart, onWillUnmount, useState, useSubEnv} from "@odoo/owl";
import {parseDate, serializeDate} from "@web/core/l10n/dates";
import {useBus, useService} from "@web/core/utils/hooks";
import {DateTimeInput} from "@web/core/datetime/datetime_input";
import {SearchBar} from "@web/search/search_bar/search_bar";
import {SearchModel} from "@web/search/search_model";
import {formatMonetary} from "@web/views/fields/formatters";
import {registry} from "@web/core/registry";

export class ReportBuilderValue extends Component {
    get formattedValue() {
        const {value, currency_id} = this.props;
        if (value && value.total) {
            return formatMonetary(value.total, {currencyId: currency_id[0]});
        }
        return "";
    }
}
ReportBuilderValue.template = "report_builder.ReportBuilderValue";
ReportBuilderValue.props = {
    value: {type: Object},
    currency_id: {type: Object, optional: true},
};

export class ReportBuilder extends Component {
    setup() {
        super.setup();
        this.state = useState({date: false, data: {}});
        this.orm = useService("orm");
        this.view = useService("view");
        this.dialog = useService("dialog");
        this.bus_service = useService("bus_service");
        this.action_service = useService("action");
        useSubEnv({
            searchModel: new SearchModel(this.env, {
                orm: this.orm,
                view: this.view,
                dialog: this.dialog,
            }),
        });
        useBus(this.env.searchModel, "update", async () => {
            await this.env.searchModel.sectionsPromise;
            this.updateData();
        });
        onWillStart(this.onWillStart);
        onWillUnmount(() => {
            this.bus_service.deleteChannel("report_builder");
        });
    }
    async onWillStart() {
        this.state.pivot_date = parseDate(this.props.record.data.data.date);
        if (this.showSearchBar) {
            await this.env.searchModel.load({
                resModel: this.props.record.data.search_res_model,
                searchViewId: this.props.record.data.search_view_id[0],
            });
        }
        this.updateData();
    }
    get showSearchBar() {
        return (
            this.props.record.data.show_search_bar &&
            this.props.record.data.search_res_model &&
            this.props.record.data.search_view_id
        );
    }
    async updateData() {
        const domain = this.showSearchBar ? this.env.searchModel.domain : [];
        const data = await this.orm.call(
            this.props.record.model.config.resModel,
            "process_information",
            [this.props.record.resIds, serializeDate(this.state.pivot_date), domain]
        );
        this.state.data = data;
    }
    onPivotDateChanged(pivot_date) {
        this.state.pivot_date = pivot_date;
        this.updateData();
    }
    refresh() {
        this.updateData();
    }
    async printPdf() {
        this.action_service.doAction(
            await this.orm.call(
                this.props.record.model.config.resModel,
                "get_pdf_report_action",
                [
                    this.props.record.resIds[0],
                    serializeDate(this.state.pivot_date),
                    this.env.searchModel.domain,
                ]
            )
        );
    }
    async printXlsx() {
        this.action_service.doAction(
            await this.orm.call(
                this.props.record.model.config.resModel,
                "get_xlsx_report_action",
                [
                    this.props.record.resIds[0],
                    serializeDate(this.state.pivot_date),
                    this.env.searchModel.domain,
                ]
            )
        );
    }
    async displaySettings() {
        this.action_service.doAction(
            await this.orm.call(
                this.props.record.model.config.resModel,
                "get_display_settings_action",
                [this.props.record.resIds[0]]
            )
        );
    }
}

ReportBuilder.components = {SearchBar, DateTimeInput, ReportBuilderValue};
ReportBuilder.template = "report_builder.ReportBuilder";

export const reportBuilder = {
    component: ReportBuilder,
    fieldDependencies: [
        {name: "name", type: "char"},
        {name: "data", type: "json"},
        {name: "currency_id", type: "many2one", relation: "res.currency"},
        {name: "show_search_bar", type: "boolean"},
        {name: "search_view_id", type: "many2one"},
        {name: "search_res_model", type: "char"},
        {name: "show_settings", type: "boolean"},
        {name: "show_pivot_date", type: "boolean"},
    ],
};

registry.category("fields").add("report_builder", reportBuilder);
