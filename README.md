[![Runbot Status](https://runbot.odoo-community.org/runbot/badge/flat/143/13.0.svg)](https://runbot.odoo-community.org/runbot/repo/github-com-oca-reporting-engine-143)
[![Build Status](https://travis-ci.com/OCA/reporting-engine.svg?branch=13.0)](https://travis-ci.com/OCA/reporting-engine)
[![codecov](https://codecov.io/gh/OCA/reporting-engine/branch/13.0/graph/badge.svg)](https://codecov.io/gh/OCA/reporting-engine)
[![Translation Status](https://translation.odoo-community.org/widgets/reporting-engine-13-0/-/svg-badge.svg)](https://translation.odoo-community.org/engage/reporting-engine-13-0/?utm_source=widget)

<!-- /!\ do not modify above this line -->

# OCA alternative reporting engines and reporting utilities for Odoo

This repository hosts alternative reporting engines to the ones included on Odoo core (RML, QWeb and Webkit).

The convention is to use a suffix to each module to indicate that it's for using with that report engine (for example, account_invoice_report_birt or sale_order_report_pentaho).

It can contain also another utilities directly involved with reports (like merge/split utils, checkers, signing tools and so on).

<!-- /!\ do not modify below this line -->

<!-- prettier-ignore-start -->

[//]: # (addons)

This part will be replaced when running the oca-gen-addons-table script from OCA/maintainer-tools.

[//]: # (end addons)

<!-- prettier-ignore-end -->

## Licenses

This repository is licensed under [AGPL-3.0](LICENSE).

However, each module can have a totally different license, as long as they adhere to OCA
policy. Consult each module's `__manifest__.py` file, which contains a `license` key
that explains its license.

----

OCA, or the [Odoo Community Association](http://odoo-community.org/), is a nonprofit
organization whose mission is to support the collaborative development of Odoo features
and promote its widespread use.
