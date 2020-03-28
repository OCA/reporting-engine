.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.png
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================
BI Views aggregate
==================

This module extends the functionality of bi_sql_editor, to support creation
custom aggregation for float and integer values.

After the model is generated, before creating the UI, the option is given
to define aggregation - either Sum (Default), Average, Minimum, or Maximum.

Configuration
=============

No configuration is required after installation.

Usage
=====

To use this module, you need to adjust the aggregation on the custom fields
tab of the sql_view between validating the SQL

#. Go to 'Reporting' / 'Custom Reports'

Known issues / Roadmap
======================

* Can be integrated with bi_sql_editor, but breaks for existing sites.
* Would be good to integrate and remove need for additional install.

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smash it by providing detailed and welcomed feedback.

Credits
=======

Contributors
------------

* Richard deMeester, Willdoo IT (http://www.willdooit.com/)

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit https://odoo-community.org.
