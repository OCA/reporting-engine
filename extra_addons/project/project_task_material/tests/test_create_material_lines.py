# Copyright 2016 Tecnativa - Vicent Cubells
# Copyright 2018 - Brain-tec AG - Carlos Jesus Cebrian
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl-3.0).

from .common import TestProjectCases
from odoo.exceptions import ValidationError


class ProjectTaskMaterial(TestProjectCases):

    def test_manager_add_task_material_wrong(self):
        """
        TEST CASE 1
        The user is adding some materials in the task
        with different wrong values

        """
        try:
            # Material with `quantity = 0.0`
            self.action.write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": 0.0})]})
        except ValidationError as err:
            self.assertEqual(
                str(err.args[0]),
                "Quantity of material consumed must be greater than 0.")

        try:
            # Material with `negative quantity`
            self.action.write({"material_ids": [(
                0, 0, {"product_id": self.product.id, "quantity": -10.0})]})
        except ValidationError as err:
            self.assertEqual(
                str(err.args[0]),
                "Quantity of material consumed must be greater than 0.")

    def test_manager_add_task_material_right(self):
        """
        TEST CASE 2
        The user is adding some materials in the task
        with right values

        """
        # Material with `quantity = 1.0`
        self.action.write({"material_ids": [(
            0, 0, {"product_id": self.product.id, "quantity": 4.0})]})
        self.assertEqual(len(self.task.material_ids.ids), 1)
