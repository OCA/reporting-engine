.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

==============
Chrome reports
==============

This module was written to make it possible to use `Chrome <https://www.google.com/chrome/browser/desktop/index.html>`_ or `Chromium <https://www.chromium.org/getting-involved/download-chromium>`_ in `headless mode <https://chromium.googlesource.com/chromium/src/+/lkgr/headless/README.md>`_ to render PDF reports. This allows you to use way more modern CSS for rendering the PDF, in the future hopefully enabling some things `CSS3 adds <https://drafts.csswg.org/css-page-3/>`_.

Installation
============

To install this module, you need to:

#. install the `cproto` module: ``pip install cproto``
#. install the version of Chrom{e,ium} you want to use

Configuration
=============

The addon wil search for a chrome binary in the ``PATH`` and Odoo's ``bin_path`` configuration setting. If your chrome binary is located somewhere else, set the config parameter ``report_qweb_chrome_renderer.chrome_bin``.

By default, Odoo communicates with Chrome via localhost:9222, if you need to set a different port, set config parameter ``report_qweb_chrome_renderer.chrome_port``.

This module already passes a bunch of parameter to Chrome to make it work in the first place, if you need to add more parameters, set ``report_qweb_chrome_renderer.chrome_extra_parameters``.

Usage
=====

To use this module, you need to:

#. create a report as usual, but set the flag `is_chrome_pdf` on the ir.actions.report.xml record
#. note that this module avoids all the hacks for wkhtmltopdf, so your report will be passed to the browser exactly as it's rendered from qweb

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/143/9.0

Known issues / Roadmap
======================

* it should be possible to emulate wkhtmltopdf's behavior and use Chrome exclusively
* provide a layout that includes some optional divs for headers, footers, page counter etc
* provide some nice internal and external layouts
* support all report features
* support paper formats
* use --remote-debugging-fd instead of port

Bug Tracker
===========

Bugs are tracked on `GitHub Issues
<https://github.com/OCA/reporting-engine/issues>`_. In case of trouble, please
check there if your issue has already been reported. If you spotted it first,
help us smashing it by providing a detailed and welcomed feedback.

Credits
=======

Images
------

* Odoo Community Association: `Icon <https://github.com/OCA/maintainer-tools/blob/master/template/module/static/description/icon.svg>`_.

Contributors
------------

* Holger Brunn <hbrunn@therp.nl>
* Ruud Verbeek <rverbeek@therp.nl>

Do not contact contributors directly about help with questions or problems concerning this addon, but use the `community mailing list <mailto:community@mail.odoo.com>`_ or the `appropriate specialized mailinglist <https://odoo-community.org/groups>`_ for help, and the bug tracker linked in `Bug Tracker`_ above for technical issues.

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
