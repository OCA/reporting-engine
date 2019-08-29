# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import io
import ast
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ReportHeaderFooter(models.Model):
    _name = 'report.xlsx.hf'

    name = fields.Char(string="Name", required=True)
    hf_type = fields.Selection(
        [('header', 'Header'), ('footer', 'Footer')],
        string="Type",
        required=True)
    value = fields.Char(string="Value")
    manual_options = fields.Char(string="Options")
    image_left = fields.Binary(string='Image left')
    image_left_name = fields.Char('File Name')
    image_center = fields.Binary(string='Image center')
    image_center_name = fields.Char('File Name')
    image_right = fields.Binary(string='Image right')
    image_right_name = fields.Char('File Name')
    header_report_ids = fields.One2many(
        'ir.actions.report.xml',
        'header_id',
        string="Associated report(s)")
    footer_report_ids = fields.One2many(
        'ir.actions.report.xml',
        'footer_id',
        string="Associated report(s)")

    @api.multi
    @api.constrains('manual_options')
    def _check_manual_options(self):
        for rec in self:
            if rec.manual_options:
                options = ast.literal_eval(rec.manual_options)
                if not isinstance(options, dict):
                    raise ValidationError(
                        _('The Header/Footer is not configured properly.\
                                     Options must be a dictionary.'))

    @api.multi
    @api.constrains('image_left', 'image_center', 'image_right')
    def _check_images(self):
        for rec in self:
            error = ""
            if rec.image_left and ("&L&G" not in rec.value
                                   and "&L&[Picture]" not in rec.value):
                error += _('You must specify the control character &L&G or \
                &L&[Picture] in the "Value" when you add an "Image left".\n')
            if rec.image_center and ("&C&G" not in rec.value
                                     and "&C&[Picture]" not in rec.value):
                error += _('You must specify the control character &C&G or \
                &C&[Picture] in the "Value" when you add an "Image center".\n')
            if rec.image_right and ("&R&G" not in rec.value
                                    and "&R&[Picture]" not in rec.value):
                error += _('You must specify the control character &R&G or \
                &R&[Picture] in the "Value" when you add an "Image right".\n')
            if error:
                raise ValidationError(error)

    @api.multi
    def get_options(self):
        self.ensure_one()
        options = {}
        if self.manual_options:
            options = ast.literal_eval(self.manual_options)
        if self.image_left:
            options['image_left'] = self.image_left_name
            options['image_data_left'] = io.BytesIO(
                self.image_left.decode('base64'))
        if self.image_center:
            options['image_center'] = self.image_center_name
            options['image_data_center'] = io.BytesIO(
                self.image_center.decode('base64'))
        if self.image_right:
            options['image_right'] = self.image_right_name
            options['image_data_right'] = io.BytesIO(
                self.image_right.decode('base64'))
        return options
