This module includes a comprehensive test suite covering:

- Printed flag assignment
- Report configuration filtering
- Multi-record batch processing
- Multi-company isolation
- Log creation and validation
- Safe execution on models without a ``printed`` field

Tests are implemented using:

- ``BaseCommon``
- ``odoo_test_helper.FakeModelLoader``

To run tests:

::

    odoo-bin -d <db> -i report_printed_flag --test-enable