Inherit the model:

.. code-block:: python

    from odoo import models

    class MyModel(models.model)
        _name = 'my.model'
        _inherit = ['sql.request.mixin']

        _sql_request_groups_relation = 'my_model_groups_rel'

        _sql_request_users_relation = 'my_model_users_rel'


See implementations in the modules ``bi_sql_editor`` and ``sql_export``. (same OCA/reporting-engine repository)
