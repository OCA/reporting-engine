=======================
MuK Large Objects Field
=======================

PostgreSQL offers support for large objects, which provide stream-style access
to user data that is stored in a special large-object structure. They are useful
with data values too large to be manipulated conveniently as a whole.

Psycopg allows access to the large object using the `lobject` class. Objects are
generated using the `connection.lobject()` factory method. Data can be retrieved
either as bytes or as Unicode strings.

Psycopg large object support efficient import/export with file system files using
the `lo_import()` and `lo_export()` libpq functions.

Changed in version 2.6: added support for large objects greated than 2GB. Note
that the support is enabled only if all the following conditions are verified:

* the Python build is 64 bits;
* the extension was built against at least libpq 9.3;
* the server version is at least PostgreSQL 9.3 (server_version must be >= 90300).

If Psycopg was built with 64 bits large objects support (i.e. the first two
contidions above are verified), the `psycopg2.__version__` constant will contain
the lo64 flag. If any of the contition is not met several lobject methods will
fail if the arguments exceed 2GB.

Installation
============

To install this module, you need to:

Download the module and add it to your Odoo addons folder. Afterward, log on to
your Odoo server and go to the Apps menu. Trigger the debug mode and update the
list by clicking on the "Update Apps List" link. Now install the module by
clicking on the install button.

Another way to install this module is via the package management for Python
(`PyPI <https://pypi.org/project/pip/>`_).

To install our modules using the package manager make sure
`odoo-autodiscover <https://pypi.org/project/odoo-autodiscover/>`_ is installed
correctly. Then open a console and install the module by entering the following
command:

``pip install --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

The module name consists of the Odoo version and the module name, where
underscores are replaced by a dash.

**Module:** 

``odoo<version>-addon-<module_name>``

**Example:**

``sudo -H pip3 install --extra-index-url https://nexus.mukit.at/repository/odoo/simple odoo11-addon-muk-utils``

Once the installation has been successfully completed, the app is already in the
correct folder. Log on to your Odoo server and go to the Apps menu. Trigger the 
debug mode and update the list by clicking on the "Update Apps List" link. Now
install the module by clicking on the install button.

The biggest advantage of this variant is that you can now also update the app
using the "pip" command. To do this, enter the following command in your console:

``pip install --upgrade --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in 
Odoo. The steps are the same as for the installation only the button has changed
from "Install" to "Upgrade".

You can also view available Apps directly in our `repository <https://nexus.mukit.at/#browse/browse:odoo>`_
and find a more detailed installation guide on our `website <https://mukit.at/page/open-source>`_.

For modules licensed under OPL-1, you will receive access data when you purchase
the module. If the modules were not purchased directly from
`MuK IT <https://www.mukit.at/>`_ please contact our support (support@mukit.at)
with a confirmation of purchase to receive the corresponding access data.

Upgrade
============

To upgrade this module, you need to:

Download the module and add it to your Odoo addons folder. Restart the server
and log on to your Odoo server. Select the Apps menu and upgrade the module by
clicking on the upgrade button.

If you installed the module using the "pip" command, you can also update the
module in the same way. Just type the following command into the console:

``pip install --upgrade --extra-index-url https://nexus.mukit.at/repository/odoo/simple <module>``

When the process is finished, restart your server and update the application in 
Odoo, just like you would normally.

Configuration
=============

No additional configuration is needed to use this module.

Usage
=============

This module has no direct visible effect on the system. It adds a new field type,
which can be used in other modules.

Credits
=======

Contributors
------------

* Mathias Markl <mathias.markl@mukit.at>

Images
------------

Some pictures are based on or inspired by the icon set of Font Awesome:

* `Font Awesome <https://fontawesome.com>`_

Author & Maintainer
-------------------

This module is maintained by the `MuK IT GmbH <https://www.mukit.at/>`_.

MuK IT is an Austrian company specialized in customizing and extending Odoo.
We develop custom solutions for your individual needs to help you focus on
your strength and expertise to grow your business.

If you want to get in touch please contact us via mail
(sale@mukit.at) or visit our website (https://mukit.at).
