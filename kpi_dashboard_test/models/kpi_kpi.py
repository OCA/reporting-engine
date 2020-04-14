# Copyright 2020 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models
import random


class KpiKpi(models.Model):
    _inherit = "kpi.kpi"

    def test_demo_number(self):
        return {
            "value": random.random() * 10000,
            "previous": random.random() * 10000,
        }

    def test_demo_meter(self):
        return {
            "min": 0,
            "max": 100,
            "value": random.random() * 100,
        }

    def test_demo_graph(self):
        return {
            "graphs": [
                {
                    "values": [
                        {"x": i, "y": random.random() * 1000}
                        for i in range(1, 12)
                    ],
                    "title": "Current Year",
                    "key": "current",
                    "area": True,
                    "color": "ffffff",
                },
                {
                    "values": [
                        {"x": i, "y": random.random() * 1000}
                        for i in range(1, 12)
                    ],
                    "title": "Previous Year",
                    "key": "previous",
                    "area": True,
                    "color": "000000",
                },
            ]
        }
