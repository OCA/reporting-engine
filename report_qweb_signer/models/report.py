# -*- coding: utf-8 -*-
# Copyright 2015 Tecnativa - Antonio Espinosa
# Copyright 2017 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from contextlib import closing
import os
import subprocess
import tempfile
import time

from odoo import models, api, _
from odoo.exceptions import UserError, AccessError
from odoo.tools.safe_eval import safe_eval

import logging
_logger = logging.getLogger(__name__)


def _normalize_filepath(path):
    path = path or ''
    path = path.strip()
    if not os.path.isabs(path):
        me = os.path.dirname(__file__)
        path = '{}/../static/certificate/'.format(me) + path
    path = os.path.normpath(path)
    return path if os.path.exists(path) else False


class Report(models.Model):
    _inherit = 'report'

    def _certificate_get(self, report, docids):
        """Obtain the proper certificate for the report and the conditions."""
        if report.report_type != 'qweb-pdf':
            return False
        certificates = self.env['report.certificate'].search([
            ('company_id', '=', self.env.user.company_id.id),
            ('model_id', '=', report.model),
        ])
        if not certificates:
            return False
        for cert in certificates:
            # Check allow only one document
            if cert.allow_only_one and len(self) > 1:
                _logger.debug(
                    "Certificate '%s' allows only one document, "
                    "but printing %d documents",
                    cert.name, len(docids))
                continue
            # Check domain
            if cert.domain:
                domain = [('id', 'in', tuple(docids))]
                domain = domain + safe_eval(cert.domain)
                docs = self.env[cert.model_id.model].search(domain)
                if not docs:
                    _logger.debug(
                        "Certificate '%s' domain not satisfied", cert.name)
                    continue
            # Certificate match!
            return cert
        return False

    def _attach_filename_get(self, docids, certificate):
        if len(docids) != 1:
            return False
        doc = self.env[certificate.model_id.model].browse(docids[0])
        return safe_eval(certificate.attachment, {
            'object': doc,
            'time': time
        })

    def _attach_signed_read(self, docids, certificate):
        if len(docids) != 1:
            return False
        filename = self._attach_filename_get(docids, certificate)
        if not filename:
            return False
        attachment = self.env['ir.attachment'].search([
            ('datas_fname', '=', filename),
            ('res_model', '=', certificate.model_id.model),
            ('res_id', '=', docids[0]),
        ], limit=1)
        if attachment:
            return base64.decodestring(attachment.datas)
        return False

    def _attach_signed_write(self, docids, certificate, signed):
        if len(docids) != 1:
            return False
        filename = self._attach_filename_get(docids, certificate)
        if not filename:
            return False
        try:
            attachment = self.env['ir.attachment'].create({
                'name': filename,
                'datas': base64.encodestring(signed),
                'datas_fname': filename,
                'res_model': certificate.model_id.model,
                'res_id': docids[0],
            })
        except AccessError:
            raise UserError(
                _('Saving signed report (PDF): '
                  'You do not have enough access rights to save attachments'))
        return attachment

    def _signer_bin(self, opts):
        me = os.path.dirname(__file__)
        java_bin = 'java -jar -Xms4M -Xmx4M'
        jar = '{}/../static/jar/jPdfSign.jar'.format(me)
        return '%s %s %s' % (java_bin, jar, opts)

    def pdf_sign(self, pdf, certificate):
        pdfsigned = pdf + '.signed.pdf'
        p12 = _normalize_filepath(certificate.path)
        passwd = _normalize_filepath(certificate.password_file)
        if not (p12 and passwd):
            raise UserError(
                _('Signing report (PDF): '
                  'Certificate or password file not found'))
        signer_opts = '"%s" "%s" "%s" "%s"' % (p12, pdf, pdfsigned, passwd)
        signer = self._signer_bin(signer_opts)
        process = subprocess.Popen(
            signer, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        if process.returncode:
            raise UserError(
                _('Signing report (PDF): jPdfSign failed (error code: %s). '
                  'Message: %s. Output: %s') %
                (process.returncode, err, out))
        return pdfsigned

    @api.model
    def get_pdf(self, docids, report_name, html=None, data=None):
        report = self._get_report_from_name(report_name)
        certificate = self._certificate_get(report, docids)
        if certificate and certificate.attachment:
            signed_content = self._attach_signed_read(docids, certificate)
            if signed_content:
                _logger.debug(
                    "The signed PDF document '%s/%s' was loaded from the "
                    "database", report_name, docids,
                )
                return signed_content
        content = super(Report, self).get_pdf(
            docids, report_name, html=html, data=data,
        )
        if certificate:
            # Creating temporary origin PDF
            pdf_fd, pdf = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.')
            with closing(os.fdopen(pdf_fd, 'w')) as pf:
                pf.write(content)
            _logger.debug(
                "Signing PDF document '%s' for IDs %s with certificate '%s'",
                report_name, docids, certificate.name,
            )
            signed = self.pdf_sign(pdf, certificate)
            # Read signed PDF
            if os.path.exists(signed):
                with open(signed, 'rb') as pf:
                    content = pf.read()
            # Manual cleanup of the temporary files
            for fname in (pdf, signed):
                try:
                    os.unlink(fname)
                except (OSError, IOError):
                    _logger.error('Error when trying to remove file %s', fname)
            if certificate.attachment:
                self._attach_signed_write(docids, certificate, content)
        return content
