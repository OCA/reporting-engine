# -*- coding: utf-8 -*-
# © 2015 Antiun Ingenieria S.L. - Antonio Espinosa
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import base64
from contextlib import closing
import os
import subprocess
import tempfile
import time

from openerp import models, api, _
from openerp.exceptions import Warning, AccessError
from openerp.tools.safe_eval import safe_eval

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

    def _certificate_get(self, cr, uid, ids, report, context=None):
        if report.report_type != 'qweb-pdf':
            _logger.info(
                "Can only sign qweb-pdf reports, this one is '%s' type",
                report.report_type)
            return False
        m_cert = self.pool['report.certificate']
        company_id = self.pool['res.users']._get_company(cr, uid)
        certificate_ids = m_cert.search(cr, uid, [
            ('company_id', '=', company_id),
            ('model_id', '=', report.model)], context=context)
        if not certificate_ids:
            _logger.info(
                "No PDF certificate found for report '%s'",
                report.report_name)
            return False
        for cert in m_cert.browse(cr, uid, certificate_ids, context=context):
            # Check allow only one document
            if cert.allow_only_one and len(ids) > 1:
                _logger.info(
                    "Certificate '%s' allows only one document, "
                    "but printing %d documents",
                    cert.name, len(ids))
                continue
            # Check domain
            if cert.domain:
                m_model = self.pool[cert.model_id.model]
                domain = [('id', 'in', tuple(ids))]
                domain = domain + safe_eval(cert.domain)
                doc_ids = m_model.search(cr, uid, domain, context=context)
                if not doc_ids:
                    _logger.info(
                        "Certificate '%s' domain not satisfied", cert.name)
                    continue
            # Certificate match!
            return cert
        return False

    def _attach_filename_get(self, cr, uid, ids, certificate, context=None):
        if len(ids) != 1:
            return False
        obj = self.pool[certificate.model_id.model].browse(cr, uid, ids[0])
        filename = safe_eval(certificate.attachment, {
            'object': obj,
            'time': time
        })
        return filename

    def _attach_signed_read(self, cr, uid, ids, certificate, context=None):
        if len(ids) != 1:
            return False
        filename = self._attach_filename_get(
            cr, uid, ids, certificate, context=context)
        if not filename:
            return False
        signed = False
        m_attachment = self.pool['ir.attachment']
        attach_ids = m_attachment.search(cr, uid, [
            ('datas_fname', '=', filename),
            ('res_model', '=', certificate.model_id.model),
            ('res_id', '=', ids[0])
        ])
        if attach_ids:
            signed = m_attachment.browse(cr, uid, attach_ids[0]).datas
            signed = base64.decodestring(signed)
        return signed

    def _attach_signed_write(self, cr, uid, ids, certificate, signed,
                             context=None):
        if len(ids) != 1:
            return False
        filename = self._attach_filename_get(
            cr, uid, ids, certificate, context=context)
        if not filename:
            return False
        m_attachment = self.pool['ir.attachment']
        try:
            attach_id = m_attachment.create(cr, uid, {
                'name': filename,
                'datas': base64.encodestring(signed),
                'datas_fname': filename,
                'res_model': certificate.model_id.model,
                'res_id': ids[0],
            })
        except AccessError:
            raise Warning(
                _('Saving signed report (PDF): '
                  'You do not have enought access rights to save attachments'))
        else:
            _logger.info(
                "The signed PDF document '%s' is now saved in the database",
                filename)
        return attach_id

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
            raise Warning(
                _('Signing report (PDF): '
                  'Certificate or password file not found'))
        signer_opts = '"%s" "%s" "%s" "%s"' % (p12, pdf, pdfsigned, passwd)
        signer = self._signer_bin(signer_opts)
        process = subprocess.Popen(
            signer, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        out, err = process.communicate()
        if process.returncode:
            raise Warning(
                _('Signing report (PDF): jPdfSign failed (error code: %s). '
                  'Message: %s. Output: %s') %
                (process.returncode, err, out))
        return pdfsigned

    @api.v7
    def get_pdf(self, cr, uid, ids, report_name, html=None, data=None,
                context=None):
        signed_content = False
        report = self._get_report_from_name(cr, uid, report_name)
        certificate = self._certificate_get(
            cr, uid, ids, report, context=context)
        if certificate and certificate.attachment:
            signed_content = self._attach_signed_read(
                cr, uid, ids, certificate, context=context)
            if signed_content:
                _logger.info("The signed PDF document '%s/%s' was loaded from "
                             "the database", report_name, ids)
                return signed_content
        content = super(Report, self).get_pdf(
            cr, uid, ids, report_name, html=html, data=data,
            context=context)
        if certificate:
            # Creating temporary origin PDF
            pdf_fd, pdf = tempfile.mkstemp(
                suffix='.pdf', prefix='report.tmp.')
            with closing(os.fdopen(pdf_fd, 'w')) as pf:
                pf.write(content)
            _logger.info(
                "Signing PDF document '%s/%s' with certificate '%s'",
                report_name, ids, certificate.name)
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
                self._attach_signed_write(
                    cr, uid, ids, certificate, content, context=context)
        return content
