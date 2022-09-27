Known issues:

* `wkhtmltopdf` doesn't always respect dpi, and mm measures don't match. For
  this matter, it's recommended to use this module along with
  `report_wkhtmltopdf_param` and enable `--disable-smart-shrinking`.

* This module depends on `base_automation` only because this module extends
  `ir.actions.server` with a new kind of action, and `base.automation` inherits
  from `ir.actions.server` by delegation in such a way that the modules cannot
  be loaded in another order.
