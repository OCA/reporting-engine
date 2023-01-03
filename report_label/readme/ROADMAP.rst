Known issues:

* This module depends on `base_automation` only because this module extends
  `ir.actions.server` with a new kind of action, and `base.automation` inherits
  from `ir.actions.server` by delegation in such a way that the modules cannot
  be loaded in another order.
  To do when migrating in version > 16 :
  1. remove  ``base_automation`` dependency
  2. install ``report_label``
  3. install then ``base_automation``.
  If the installation of ``base_automation`` works, the dependency can be
  replaced by ``base``.
