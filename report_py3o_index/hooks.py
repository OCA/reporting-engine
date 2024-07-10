# Copyright 2024 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import SUPERUSER_ID, api

_logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    _logger.info("Install index update macro with default path.")
    env = api.Environment(cr, SUPERUSER_ID, {})
    try:
        env["py3o.report"]._install_update_index_macro()
    except Exception as e:
        _logger.warn("Failed to install index update macro.")
        _logger.warn("--------")
        _logger.warn(e)
        _logger.warn("--------")
