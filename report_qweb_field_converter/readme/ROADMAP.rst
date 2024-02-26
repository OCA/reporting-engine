The Options attribute in QWeb Field Converter is meant for use in PDF reports
to prevent UI issues in web views.
For example, adding {"widget": "date"} for the date_approve field in a purchase order
can cause two dates to appear under the confirmation date column in the portal view,
due to it being defined twice with different widgets.
https://github.com/odoo/odoo/blob/5eec37961c2170b354ef837b46f94e89ebf37d52/addons/purchase/views/portal_templates.xml#L101-L102
