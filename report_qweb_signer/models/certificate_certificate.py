# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import base64

from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.x509 import load_pem_x509_certificate

from odoo import models


class CertificateCertificate(models.Model):
    _inherit = "certificate.certificate"

    def _load_signing_key_and_cert(self):
        """Return the ``(private_key, certificate)`` tuple expected by Odoo's
        standard :meth:`odoo.tools.pdf.signature.PdfSigner._load_key_and_certificate`.

        This lets us reuse the core ``PdfSigner`` while keeping the certificate
        configurable per report (instead of per company).
        """
        self.ensure_one()
        certificate = self.with_context(bin_size=False)
        cert_bytes = base64.b64decode(certificate.pem_certificate)
        private_key_bytes = base64.b64decode(certificate.private_key_id.content)
        return (
            load_pem_private_key(private_key_bytes, None),
            load_pem_x509_certificate(cert_bytes),
        )
