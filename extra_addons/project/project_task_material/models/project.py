# Copyright 2012 - 2013 Daniel Reis
# Copyright 2015 - Antiun Ingeniería S.L. - Sergio Teruel
# Copyright 2016 - Tecnativa - Vicent Cubells
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class Task(models.Model):
    """Added Material Used in the Project Task."""

    _inherit = "project.task"

    material_ids = fields.One2many(
        comodel_name='project.task.material', inverse_name='task_id',
        string='Material Used')


class ProjectTaskMaterial(models.Model):
    """Added Product and Quantity in the Task Material Used."""

    _name = "project.task.material"
    _description = "Task Material Used"

    task_id = fields.Many2one(
        comodel_name='project.task', string='Task', ondelete='cascade',
        required=True)
    product_id = fields.Many2one(
        comodel_name='product.product', string='Product', required=True)
    quantity = fields.Float(string='Quantity')

    @api.multi
    @api.constrains('quantity')
    def _check_quantity(self):
        for material in self:
            if not material.quantity > 0.0:
                raise ValidationError(
                    _('Quantity of material consumed must be greater than 0.')
                )
