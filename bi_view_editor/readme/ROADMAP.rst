* Non-stored fields and many2many fields are not supported.
* Provide a tutorial (eg. a working example of usage).
* Find better ways to extend the *_auto_init()* without override.
* Possibly avoid the monkey patches.
* Data the user has no access to (e.g. in a multi company situation) can be
  viewed by making a view. Would be nice if models available to select when
  creating a view are limited to the ones that have intersecting groups.
* As of Odoo 16, translations of the name of a BI View and of the field
  descriptions do not work as expected: the translated strings are selected
  (by the user's language) when the view is generated (and stored as their
  ``en_US`` value) instead of when it is displayed.
