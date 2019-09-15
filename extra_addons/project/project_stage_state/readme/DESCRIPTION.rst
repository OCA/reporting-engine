This module restores the `state` fields to Project Stages, removed in Odoo 8.0.

For some use cases it‘s necessary to be able to map the multiple Stages into
a few broad groups.

For example, this can allow to define automated actions and business logic for
Tasks not yet “Started”, knowing that “Started” means different Stages in
different Projects.
