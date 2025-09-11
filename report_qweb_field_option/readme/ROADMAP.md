#. QWeb field option settings only apply to fields rendered with ``t-field``.  
   They don’t work with ``t-esc`` or other expressions not using ``t-field``.

   As a workaround, you could create a module that adds a computed field holding the
   same value currently computed and displayed in the QWeb report using ``t-esc``, and
   adjust the report template to display the field value using ``t-field``. This would
   allow you to adjust the decimal precision as needed.


#. Assigning Options in a QWeb Field Options record can cause UI issues if a field is
   defined twice with different widgets in a view.

   For example, adding ``{"widget": "date"}`` to the date_approve field in a purchase 
   order can result in two dates appearing under the Confirmation Date column in the 
   portal view. This occurs because the field is defined twice with different widgets.

   Reference: https://github.com/odoo/odoo/blob/5eec379/addons/purchase/views/portal_templates.xml#L101-L102