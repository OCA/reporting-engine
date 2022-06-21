This module allows to add extra data when rendering a report. For example, if we want to use an extra field not defined in the model. It would also be useful when using py3o, as complex behaviors are not valid, for example, filtering, adding conditions...

The field code data must be written with python and it must save a dict in a variable named "result. It can access the records using the "records" variable and the ir.actions.report record using the variable "self".
Example of code_data:

.. code-block:: python

      result = {
        "field_a": records.field_1 if records.state == "draft" else records.field_2
      }
