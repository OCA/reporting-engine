In the generated reports, the fields relative to the order details are not
correctly displayed: they are both "cut" from the view, or the general
font size is scaled down to make all the element fit which is not the
default behavior. The font size should remain fixed and all the element
should be visible, eventually spanning over multiple lines.

This is due to the broken bootstrap 4 support of QtWebKit, used by
wkhtmltopdf to generate pdf reports.
In particular the new flexbox style introduced in the library is not
supported and every element based on it will be ill-displayed.

This module changes the .col-auto behavior to work similiar as in
older Odoo versions.
