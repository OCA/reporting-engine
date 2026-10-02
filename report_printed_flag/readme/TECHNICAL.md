Architecture
=============

The module uses a two-layer design:

**Layer 1: Configuration & Core Logic**

- ``report.printed.config`` — Per-model, per-company configuration
- ``report.printed.config.line`` — Per-report rules with optional domain filters
- ``ir.actions.report._render_qweb_pdf`` — Hook that applies the printed flag mechanism
- ``report.printed.log`` — Audit log using generic (res_model, res_id) references

**Layer 2: Mixin for Data Models**

- ``report.printed.mixin`` — Abstract model providing:
  - ``printed`` Boolean field
  - ``printed_log_ids`` One2many (auto-filtered by ``res_model``)
  - ``printed_report_names`` computed Char field
  - ``action_view_printed_logs()`` method

Execution Flow
==============

During PDF report generation:

1. ``ir.actions.report._render_qweb_pdf()`` is called
2. System detects the report and target model/records
3. Loads matching configurations for the current company context
4. For each record:
   - Finds matching report rule (line)
   - Evaluates optional domain condition
   - Marks record as printed if conditions match
   - Creates log entry if enabled in configuration
5. Returns standard PDF content

The domain expressions are evaluated using::

    odoo.tools.safe_eval

Generic Reference Pattern
==========================

``report.printed.log`` uses a generic (res_model, res_id) reference pattern:

- ``res_model`` (Char) — Target model name (e.g., "account.move")
- ``res_id`` (Many2oneReference) — Record ID, automatically filtered by ``res_model``

This allows a single log table to track all printed records across all models.

The ``printed_log_ids`` One2many on ``report.printed.mixin`` automatically:
- Filters logs by the model's name via ``Many2oneReference``
- Works generically across any inheriting model without hardcoded model names
- Maintains proper ORM cache invalidation for computed fields

Example: Creating an Extension Module
======================================

To add printed flag support to a custom model::

    # models/my_model.py
    from odoo import models

    class MyModel(models.Model):
        _name = 'my.model'
        _inherit = ['my.model', 'report.printed.mixin']
        
        # All printed-related fields and methods come from the mixin:
        # - printed (Boolean)
        # - printed_log_ids (One2many)
        # - printed_report_names (Char, computed)
        # - action_view_printed_logs() (method)

Then configure which reports trigger the printed flag via the UI:
Settings > Reporting > Printed Flag > Configurations