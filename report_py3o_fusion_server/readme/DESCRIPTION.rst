This module was written to connect to a local LibreOffice daemon that handle format conversion instead of spawning a new LibreOffice for each conversion. It has several advantages:

* much better performances: LibreOffice runs permanently in the background, no need to spawn a new LibreOffice instance for every document conversion.
* ability to configure PDF export options in Odoo. This brings many new possibilities such as the ability to generate:

  * PDF forms
  * PDF/A documents (required by some electronic invoicing standards such as `Factur-X <http://fnfe-mpe.org/factur-x/factur-x_en/>`_)
  * watermarked PDF documents
  * password-protected PDF documents
