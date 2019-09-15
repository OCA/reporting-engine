# Copyright 2017 - 2018 Modoolar <info@modoolar.com>
# License LGPLv3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

from mock import patch
from odoo import http
from ..controllers.main import ProjectBrowser
from .test_common import HttpTestCommon


class TestController(HttpTestCommon):
    def setUp(self):
        super(TestController, self).setUp()

    def test_01_project_browse(self):
        with patch.object(http, 'request') as request:
            request.env = self.env
            controller = ProjectBrowser()
            response = controller.open_project(self.project_1.key)

            self.assertEqual(response.status_code, 301)
            self.assertEqual(
                response.location,
                self.get_project_url(self.project_1)
            )

    def test_02_task_browse(self):
        with patch.object(http, 'request') as request:
            request.env = self.env
            controller = ProjectBrowser()
            response = controller.open_task(self.task11.key)

            self.assertEqual(response.status_code, 301)
            self.assertEqual(
                response.location,
                self.get_task_url(self.task11)
            )
