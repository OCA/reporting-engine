# Copyright 2025 Moduon Team S.L. <info@moduon.team>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl.html).
import base64
import logging
import os
import subprocess
import tempfile
from contextlib import closing

PYHANKO_BIN = os.environ.get("PYHANKO_BIN", "pyhanko")

_logger = logging.getLogger(__name__)


class PdfSigner:
    def __init__(self, content, certificate, company=None, signing_time=None) -> None:
        self.signing_time = signing_time
        self.company = company
        self.content = content
        self.certificate = certificate

    def _signer_pyhanko_cli(
        self, certificate_bytes, in_pdf, out_pdf, passphrase, field="Signature1"
    ):
        """Sign using pyHanko CLI"""
        pass_fds = ()
        try:
            # We need to write the certificate bytes to a tmp file so pyhanko-cli
            # can operate with it
            fd, temp_path = tempfile.mkstemp(suffix=".p12", prefix="cert.")
            with closing(os.fdopen(fd, "wb")) as fh:
                fh.write(certificate_bytes)
            p12_path = temp_path
            args = [
                PYHANKO_BIN,
                "sign",
                "addsig",
                "--field",
                field,
                "pkcs12",
            ]
            # We also need to write a passphrase file
            passphrase_fd, pass_temp_path = tempfile.mkstemp(
                suffix=".txt", prefix="pass."
            )
            with closing(os.fdopen(passphrase_fd, "w", encoding="utf-8")) as fh:
                fh.write(passphrase)
                fh.write("\n")
            passphrase_fd = None
            args.extend(["--passfile", pass_temp_path])
            args.extend([in_pdf, out_pdf, p12_path])
            _logger.info("Calling pyHanko CLI: %s", " ".join(args))
            subprocess.run(
                args,
                check=True,
                pass_fds=pass_fds,
            )
        finally:
            if passphrase_fd is not None:
                os.close(passphrase_fd)
            if temp_path:
                try:
                    os.unlink(temp_path)
                except OSError:
                    _logger.debug("Could not remove temp file %s", temp_path)
            if pass_temp_path:
                try:
                    os.unlink(pass_temp_path)
                except OSError:
                    _logger.debug(
                        "Could not remove passphrase temp file %s", pass_temp_path
                    )
        return out_pdf

    def _sign_pdf(self, pdf_path):
        """Inner method. We could hook here different signing methods"""
        signed_pdf_path = pdf_path[:-4] + "_signed.pdf"
        self._signer_pyhanko_cli(
            base64.b64decode(self.certificate.content),
            pdf_path,
            signed_pdf_path,
            self.certificate.pkcs12_password,
        )
        return signed_pdf_path

    def sign_pdf(self):
        """Global method, sign the pdf stream with the given certificate"""
        # We need to create a temporary PDF file so we can use it with pyhanko-cli
        pdf_fd, pdf_path = tempfile.mkstemp(suffix=".pdf", prefix="report.tmp.")
        with closing(os.fdopen(pdf_fd, "wb")) as pf:
            pf.write(self.content)
        signed_pdf_path = self._sign_pdf(pdf_path)
        # Once we have the generated file we can finally read it and throw it back
        # to memory
        if os.path.exists(signed_pdf_path):
            with open(signed_pdf_path, "rb") as pf:
                self.content = pf.read()
        # Let's clean up the tmp garbage
        for fname in (pdf_path, signed_pdf_path):
            try:
                os.unlink(fname)
            except OSError:
                _logger.error("Error when trying to remove file %s", fname)
        return self.content
