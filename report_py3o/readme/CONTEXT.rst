The mixin in the report_py3o module allows to set up a Py3o template at 
both model and registry level. This significantly extends the capabilities of the 
report_py3o module, allowing an efficient and centralised customisation of reports in Odoo.

The mixin allows:

* Model Level Management: Associate a default template to a model, so that all its records 
  can use it as a basis for report generation.
* Customisation by Record: Allow each individual record to have its own unique template, 
  tailored to specific needs.
* Use of Reports with dynamic template: Use a generic report that, thanks to the mixin, 
  can dynamically adjust the Py3o template according to the model or record being processed.
