.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

=======================
Qweb PDF reports signer
=======================

This module extends the functionality of report module to sign
PDFs using a PKCS#12 certificate.


Installation
============

To install this module, you need to install Java JDK::

  apt-get install openjdk-7-jre-headless


Configuration
=============

In order to start signing PDF documents you need to configure certificate(s)
to use in your company.

* Go to ``Settings > Companies > Companies > Your company``
* Go to ``Report configuration`` tab
* Click ``Edit``
* Add a new item in ``PDF report certificates`` list
* Click ``Create``
* Set name, certificate file, password file and model
* Optionally you can set a domain and filename pattern for saving as attachment

For example, if you want to sign only customer invoices in open or paid state:

* Model: ``account.invoice``
* Domain: ``[('type','=','out_invoice'), ('state', 'in', ('open', 'paid'))]``
* Save as attachment: ``(object.number or '').replace('/','_') + '.signed.pdf'``

**Note**: Linux user that executes Odoo server process must have
read access to certificate file and password file


Usage
=====

User just prints PDF documents (only Qweb PDF reports supported) as usual,
but signed PDF is automatically downloaded if this document model is configured
as indicated above.

If 'Save as attachment' is configured, signed PDF is saved as attachment and
next time saved one is downloaded without signing again. This is appropiate when
signing date is important, for example, when signing customer invoices.

.. image:: https://odoo-community.org/website/image/ir.attachment/5784_f2813bd/datas
   :alt: Try me on Runbot
   :target: https://runbot.odoo-community.org/runbot/143/8.0

For further information, please visit:

* https://www.odoo.com/forum/help-1


Known issues / Roadmap
======================

* When signing multiple documents (if 'Allow only one document' is disable)
  then 'Save as attachment' is not applied and signed result is not
  saved as attachment.
* To have a visible signature through an image embedded in the resulting PDF.


Bug Tracker
===========

Bugs are tracked on `GitHub Issues <https://github.com/OCA/reporting-engine/issues>`_.
In case of trouble, please check there if your issue has already been reported.
If you spotted it first, help us smashing it by providing a detailed and welcomed feedback
`here <https://github.com/OCA/reporting-engine/issues/new?body=module:%20report_qweb_signer%0Aversion:%208.0%0A%0A**Steps%20to%20reproduce**%0A-%20...%0A%0A**Current%20behavior**%0A%0A**Expected%20behavior**>`_.


Credits
=======

External utilities
------------------

* iText v1.4.8: © 2000-2006, Paulo Soares, Bruno Lowagie and others - License `MPL <http://www.mozilla.org/MPL>`_ or `LGPL2 <http://www.gnu.org/licenses/old-licenses/lgpl-2.0.html>`_ - http://sourceforge.net/projects/itext
* jPdfSign: © 2006 Jan Peter Stotz - License `MPL <http://www.mozilla.org/MPL>`_ or `LGPL2 <http://www.gnu.org/licenses/old-licenses/lgpl-2.0.html>`_ (inherited from iText) - http://private.sit.fraunhofer.de/~stotz/software/jpdfsign
* Modified jPdfSign: © 2015 Antonio Espinosa - License `MPL <http://www.mozilla.org/MPL>`_ or `LGPL2 <http://www.gnu.org/licenses/old-licenses/lgpl-2.0.html>`_ (inherited from iText) - static/src/java/JPdfSign.java

Icon
----

`Created by Anton Noskov from the Noun Project <https://thenounproject.com/search/?q=signed+contract&i=65694>`_

Contributors
------------

* Rafael Blasco <rafabn@antiun.com>
* Antonio Espinosa <antonioea@antiun.com>

Maintainer
----------

.. image:: https://odoo-community.org/logo.png
   :alt: Odoo Community Association
   :target: https://odoo-community.org

This module is maintained by the OCA.

OCA, or the Odoo Community Association, is a nonprofit organization whose
mission is to support the collaborative development of Odoo features and
promote its widespread use.

To contribute to this module, please visit http://odoo-community.org.
