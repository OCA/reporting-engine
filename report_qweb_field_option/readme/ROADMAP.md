Assigning Options in a QWeb Field Options record can cause UI issues if
a field is defined twice with different widgets in a view.

For example, adding `{"widget": "date"}` to the date_approve field in a
purchase order can result in two dates appearing under the Confirmation
Date column in the portal view. This occurs because the field is defined
twice with different widgets.

Reference:
<https://github.com/odoo/odoo/blob/5eec379/addons/purchase/views/portal_templates.xml#L101-L102>
