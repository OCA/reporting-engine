This module extends `sql_export` to add Excel (`.xlsx`) as an output
format. Two modes are available: generating a fresh Excel file from
the query results, or inserting the results into a pre-defined Excel
template.

**Generate a fresh Excel file**

1.  Open an existing SQL export query, or create a new one as
    documented in `sql_export`.
2.  Define the SQL query.
3.  Run the export and select the Excel output. The resulting
    `.xlsx` contains the column headers (if enabled) and one row per
    result row.

**Insert results into an Excel template**

This mode is useful when the final report relies on Excel formulas,
charts, or formatting that should be preserved across exports.

1.  Prepare your `.xlsx` template locally. Leave empty the cells where
    the query results should be written.
2.  Attach the template file to the query record.
3.  Configure where the data should be inserted: target sheet, start
    row, start column, and whether to include the header row.
4.  Run the export. The template is opened, the query results are
    written at the configured position, and the updated file is
    returned.

Any formulas or charts in the template that reference the inserted
cells are recalculated when the file is opened.

**Example: monthly sales summary**

A typical use case is a recurring report where the layout and
calculations live in Excel, and only the raw data changes.

Suppose the template `sales_summary.xlsx` contains:

-   *Sheet 1 - Data*: empty, will receive the query results.
-   *Sheet 2 - Summary*: pivot tables and charts referencing
    *Sheet 1*.

Define the SQL query, for example:

    SELECT
        partner.name AS customer,
        SUM(line.price_subtotal) AS revenue
    FROM sale_order_line line
    JOIN sale_order so ON so.id = line.order_id
    JOIN res_partner partner ON partner.id = so.partner_id
    WHERE so.state IN ('sale', 'done')
        AND so.date_order >= date_trunc('month', CURRENT_DATE)
    GROUP BY partner.name
    ORDER BY revenue DESC;

Attach `sales_summary.xlsx` to the query, set the target sheet to
*Data*, include the header, and start at row 1, column 1. Each
export then produces an up-to-date version of the report, with the
pivots and charts on *Sheet 2* refreshed automatically when the file
is opened.

**Notes**

-   The variable substitution patterns documented in `sql_export`
    (such as `%(company_id)s` and `%(user_id)s`) also apply to this
    module.
-   `jsonb` columns in the query result are serialised before being
    written to the Excel file.