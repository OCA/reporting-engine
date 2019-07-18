This module was written to let a py3o fusion server handle format conversion instead of local libreoffice. If you install this module above the *report_py3o* module, you will have to deploy additionnal software components and run 3 daemons (libreoffice, py3o.fusion and py3o.renderserver). This additionnal complexiy comes with several advantages:

* much better performances (Libreoffice runs permanently in the background, no need to spawn a new Libreoffice instance upon every document conversion).
* ability to configure PDF export options in Odoo. This brings many new possibilities such as the ability to generate:

  * PDF forms
  * PDF/A documents (required by some electronic invoicing standards such as `Factur-X <http://fnfe-mpe.org/factur-x/factur-x_en/>`_)
  * watermarked PDF documents
  * password-protected PDF documents
