# Copyright 2022 Sunflower IT (https://sunflowerweb.nl/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)

from odoo import api, models


class QueueJob(models.Model):
    _inherit = "queue.job"

    @api.model
    def create(self, values):
        res = super(QueueJob, self).create(values)
        if (
            "model_name" in values
            and values["model_name"] == "report.async"
            and "kwargs" in values
            and "to_email" in values["kwargs"]
        ):
            followers = self._find_partner(res, values["kwargs"]["to_email"])
            if followers:
                res.message_subscribe(partner_ids=followers)
        return res

    def _find_partner(self, record, email):
        partner = self.env["res.partner"].search([("email", "=", email)], limit=1)
        followers = record.message_follower_ids.mapped("partner_id")
        ids = [x for x in partner.ids if x not in followers.ids]
        if partner and ids:
            return ids
        return None
