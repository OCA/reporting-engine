This module provides a generic and extensible configuration layer to mark
records as printed when specific PDF reports are generated.

Main features:

- **Reusable Mixin** (``report.printed.mixin``) that any model can inherit to gain:
  - A ``printed`` Boolean field
  - A ``printed_log_ids`` One2many relation to audit logs
  - A ``printed_report_names`` computed field with printed report names
  - An ``action_view_printed_logs()`` method
- Generic configuration per company and model
- Per-report configuration using rules
- Optional domain conditions per report
- Automatic printed flag update
- Optional logging of report executions
- Optional computation of printed report names
- Full multi-company support with isolated configurations
- User interface for browsing printed report logs

Extension modules simply inherit the mixin:

```python
class AccountMove(models.Model):
    _name = 'account.move'
    _inherit = ['account.move', 'report.printed.mixin']
```

All printed flag functionality is inherited automatically.

Limitations:

- Only applies to QWeb PDF reports (``qweb-pdf``)
- Extension modules must inherit ``report.printed.mixin`` to gain printed field support
- Domain expressions must be valid Python domains