To configure this module, you need to:

1. Go to System parameters and create or edit `report.display_name_in_footer_models`
   parameter.

2. Add desired model names separated by comma.

   - If you want to print name on all reports, just write 'all' on the value.
   - If you want to exclude certain models, add '-' before model name.

3. Examples:

   - Only few models: sale.order,purchase.order,stock.picking
   - All models: all
   - All models except two: all,-sale.order,-purchase.order

4. The field printed in the report will be _name_ for any type of document. If your
   document doesn't have this field, please exclude from the list with '-' and the name
   of the model.

5. Compatible document layout:

   - Light
   - Boxed
   - Striped

6. Compatible report types:

   - PDF
