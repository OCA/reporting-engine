Add a new mixin class to define templates of comments to print on documents.
The comment templates can be defined like make templates, so you can use variables from linked models.

Two positions are available for the comments:

* above document lines (before_lines)
* below document lines (after_lines)

The template are general, and can be attached to any Model and based on some domain defined in the template.
You can define one default template per Model and domain, which can be overwritten for any company and partners.
It has a priority field (smaller number = higher priority)

In existing reports, if you add this line will get the comment template if you created one like

* <span t-raw="o.get_comment_template('position',company_id=o.company_id, partner_id=o.parnter_id )"/> ( or without any parameter)


This module is the base module for following modules:

* sale_comment_template
* purchase_comment_template
* invoice_comment_template
* stock_picking_comment_template
