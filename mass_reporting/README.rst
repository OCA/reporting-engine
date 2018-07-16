.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==============
MASS REPORTING
==============

This module allows you to generate a large volume of reports (like several
thousands), optionally concatenate them, and alerts users when the process is
done.
It is based on the Job queue provided by the ``connector`` framework to
process the reports, and on the standard messaging system of Odoo to send
alerts.

Installation
============

To use this module, you need to install `PyPDF2`::

    $ sudo pip install PyPDF2

Or on Debian based system::

    $ sudo apt-get install python-pypdf2

Configuration
=============

Go to the *Reporting / Mass reporting / Mass reports* menu to create a new
mass report. Here you have to set the following options:

    - set the data model from which reports should be printed (e.g. 'Invoice'),
    - select the user account used to print the reports,
    - select the reports to print in the right order (e.g. a PDF letter
      + the PDF invoice),
    - configure the filters to use (e.g. to get only validated invoices)
    - choose the output format:
        * do nothing (simple case, useful if you just want to generate your
          invoices as attachments)
        * concatenate all files into one,
        * put individual reports into a single ZIP archive
        * or implement your own output format (like sending the produced data
          by email or SFTP to another server).

Once configured, just push the "Run" button and wait. The configured user will
be notified via the Odoo messaging when the mass report is processed.
The resulting file (if any) will be available in the `File` field.

Usage
=====

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/8.0

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/server-tools/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed `feedback
<https://github.com/OCA/
server-tools/issues/new?body=module:%20
nsca_client%0Aversion:%20
8.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.

Credits
=======

Images
------

* Icon: from the `Oxygen theme <https://en.wikipedia.org/wiki/Oxygen_Project>`_ (LGPL)

Contributors
------------

* Sébastien Alix <sebastien.alix@osiell.com>

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
