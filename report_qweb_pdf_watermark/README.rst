.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=============
Pdf watermark
=============

This module was written to add watermarks (backgrounds) to PDF reports. Because of the way wkhtmltopdf handles headers and footers in the current versions, it is quite impossible to have a background for the complete page using HTML and CSS. That is why this module inserts the image at the PDF level.

Installation
============

This module works out of the box, but is faster if you install the python library PyPDF2.

Usage
=====

To use this module, you need to:

#. go to your report
#. select a PDF or image to use as watermark. Note that resolutions and size must match, otherwise you'll have funny results
#. You can also fill in an expression that returns the data (base64 encoded) to be used as watermark

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
    :alt: Try me on Runbot
    :target: https://runbot.odoo-community.org/runbot/143/8.0

Known Issues
============
This module depends on support for transparent backgrounds in Wkhtmltopdf, which has been flaky in the past. This module has been reported to work with Wkhtmltopdf 0.12.4.

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
* Stefan Rijnhart <stefan@opener.am>

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
