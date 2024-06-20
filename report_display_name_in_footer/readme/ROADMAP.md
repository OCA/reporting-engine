When this module is checking if the model has to display the name in the footer
is done at the  level of the initial model of the report you are printing.

Examples of strange cases/uses:
*stock_picking_batch_print_pickings* and *stock_picking_batch_print_invoices* modules
print the delivery notes or invoices of the Pickings associated with the Batch,
but the report is being launched from the Batch. So, the header and footer
belongs to the Batch.

Within that report, calls are made to the invoice or delivery note reports,
but the check to see if the name of the document has to be printed in the
footer is done on the Batch.

Therefore, if you set the configuration parameter to "stock.picking, account.move"
, the names printed from that report will not appear.
By setting it to "stock.picking.batch", the module will establish that all the
documents contained in that report (whether invoices or delivery notes)
must include the name in the footer.
