# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

from werkzeug.test import Client

from odoo.http import root
from odoo.tests.common import HttpCase, tagged
from odoo.tools import config, file_path

from odoo.addons.base.models import ir_actions_report as base_report

from ..models import ir_actions_report as local_assets
from ..models.ir_actions_report import AssetLocalizer

STATIC_CSS = "/web/static/src/libs/fontawesome/css/font-awesome.css"
STATIC_IMG = "/web/static/img/logo.png"


@tagged("post_install", "-at_install")
class TestLocalAssets(HttpCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.report = cls.env["ir.actions.report"]
        cls.origin = cls.report._get_report_url()
        cls.static_root = file_path("web/static")

    def setUp(self):
        super().setUp()
        self.workdir = tempfile.mkdtemp(prefix="test.report.assets.")
        self.addCleanup(shutil.rmtree, self.workdir, ignore_errors=True)

    def localizer(self, session_id=None):
        return AssetLocalizer(self.env, self.workdir, session_id)

    def written(self):
        return sorted(os.listdir(self.workdir))

    @staticmethod
    def file_url(path):
        return Path(file_path(path.lstrip("/"))).as_uri()

    def test_static_files_referenced_in_place(self):
        html = (
            f'<html><head><base href="{self.origin}/">'
            f'<link rel="stylesheet" href="{STATIC_CSS}"/>'
            f'<link rel="icon" href="{STATIC_IMG}"/></head>'
            f'<body><img src="{self.origin}{STATIC_IMG}"/></body></html>'
        )
        localizer = self.localizer()
        result = localizer.localize_html(html)
        self.assertTrue(result.startswith("<html>"))
        self.assertIn(f'href="{self.file_url(STATIC_CSS)}"', result)
        self.assertIn(f'src="{self.file_url(STATIC_IMG)}"', result)
        self.assertIn(f'<link rel="icon" href="{STATIC_IMG}">', result)
        self.assertEqual(localizer.allow_paths, {self.static_root})
        self.assertEqual(self.written(), [])

    def test_asset_bundles_fetched_in_process(self):
        bundle = self.env["ir.qweb"]._get_asset_bundle("web.report_assets_common")
        css_url, js_url = bundle.css()[0].url, bundle.js()[0].url
        html = (
            f'<html><head><link rel="stylesheet" href="{css_url}"/>'
            f'<script src="{js_url}"></script></head><body/></html>'
        )
        localizer = self.localizer()
        result = localizer.localize_html(html)
        self.assertNotIn(css_url, result)
        self.assertNotIn(js_url, result)
        css_file = next(name for name in self.written() if name.endswith(".css"))
        js_file = next(name for name in self.written() if name.endswith(".js"))
        self.assertIn(f'src="{Path(self.workdir, js_file).as_uri()}"', result)
        self.assertIn(f'href="{Path(self.workdir, css_file).as_uri()}"', result)
        css = Path(self.workdir, css_file).read_text()
        self.assertIn("url(file://", css)
        self.assertNotIn("url(/web/static/", css)
        self.assertIn(self.static_root, localizer.allow_paths)

    def test_css_relative_urls_resolved_against_stylesheet(self):
        attachment = self.env["ir.attachment"].create(
            {
                "name": "test.css",
                "public": True,
                "mimetype": "text/css",
                "raw": b"body{background:url('../static/img/logo.png')}"
                b"h1{background:url(/web/image/res.company/1/logo)}",
            }
        )
        html = (
            f'<html><head><link rel="stylesheet" href="/web/content/{attachment.id}"/>'
            f"</head><body/></html>"
        )
        self.localizer().localize_html(html)
        (css_file,) = self.written()
        self.assertEqual(
            Path(self.workdir, css_file).read_text(),
            f"body{{background:url({self.file_url(STATIC_IMG)})}}"
            "h1{background:url(/web/image/res.company/1/logo)}",
        )

    def test_inline_styles_rewritten(self):
        html = (
            f"<html><head><style>.a{{background:url({STATIC_IMG})}}</style><style/></head>"
            f"<body><div style=\"background: url( '{STATIC_IMG}' )\"/></body></html>"
        )
        result = self.localizer().localize_html(html)
        self.assertEqual(result.count(f"url({self.file_url(STATIC_IMG)})"), 2)

    def test_foreign_and_unresolvable_urls_untouched(self):
        urls = [
            "https://example.com/a.png",
            "data:image/png;base64,AAAA",
            "#anchor",
            "mailto:a@b.c",
            "/web/static/img/missing.png",
            "/web/does-not-exist",
        ]
        images = "".join(f'<img src="{url}"/>' for url in urls)
        html = f"<html><body>{images}</body></html>"
        localizer = self.localizer()
        result = localizer.localize_html(html)
        for url in urls:
            self.assertIn(f'src="{url}"', result)
        self.assertEqual(self.written(), [])
        self.assertEqual(localizer.localize_url("", self.origin), None)
        self.assertEqual(localizer.localize_html(None), None)

    def test_x_sendfile_response_untouched(self):
        attachment = self.env["ir.attachment"].create(
            {"name": "blob.bin", "public": True, "raw": b"binary"}
        )
        url = f"/web/content/{attachment.id}"
        html = f'<html><body><img src="{url}"/></body></html>'
        with patch.dict(config.options, {"x_sendfile": True}):
            result = self.localizer().localize_html(html)
        self.assertIn(f'src="{url}"', result)
        self.assertEqual(self.written(), [])

    def test_fetch_failure_untouched(self):
        url = "/web/image/res.company/1/logo"
        html = f'<html><body><img src="{url}"/></body></html>'
        with (
            patch.object(Client, "get", side_effect=RuntimeError("boom")),
            self.assertLogs(local_assets.__name__, logging.WARNING),
        ):
            result = self.localizer().localize_html(html)
        self.assertIn(f'src="{url}"', result)

    def test_repeated_url_fetched_once(self):
        url = "/web/image/res.company/1/logo"
        images = f'<img src="{url}"/><img src="{url}?unique=1"/><img src="{url}"/>'
        html = f"<html><body>{images}</body></html>"
        with patch.object(
            AssetLocalizer, "_fetch", autospec=True, wraps=AssetLocalizer._fetch
        ) as fetch:
            self.localizer().localize_html(html)
        self.assertEqual(fetch.call_count, 2)
        self.assertEqual(len(self.written()), 2)

    def test_session_grants_user_access_rights(self):
        user = self.env.ref("base.user_admin")
        attachment = self.env["ir.attachment"].create(
            {"name": "private.txt", "raw": b"private", "mimetype": "text/plain"}
        )
        url = f"/web/content/{attachment.id}"
        self.assertIsNone(self.localizer()._fetch(url))
        fake_request = SimpleNamespace(
            db=self.env.cr.dbname,
            session={"uid": user.id, "login": user.login, "db": self.env.cr.dbname},
        )
        with patch.object(local_assets, "request", fake_request):
            session = self.report.with_user(user)._wkhtmltopdf_asset_session()
        self.addCleanup(root.session_store.delete, session)
        self.assertTrue(session.session_token)
        self.assertEqual(root.session_store.get(session.sid).uid, user.id)
        self.assertEqual(
            self.localizer(session.sid)._fetch(url), ("text/plain", b"private")
        )
        self.assertIsNone(self.report._wkhtmltopdf_asset_session())

    def test_run_wkhtmltopdf_drops_temporary_session(self):
        fake_request = SimpleNamespace(
            db=self.env.cr.dbname, session={"db": self.env.cr.dbname}
        )
        with (
            patch.object(local_assets, "request", fake_request),
            patch.object(
                root.session_store, "delete", wraps=root.session_store.delete
            ) as delete,
            patch.object(
                base_report.IrActionsReport, "_run_wkhtmltopdf", return_value=b"%PDF"
            ),
        ):
            self.assertEqual(self.report._run_wkhtmltopdf(["<html/>"]), b"%PDF")
        delete.assert_called_once()
        (session,) = delete.call_args.args
        self.assertFalse(session.uid)
        self.assertIsNone(root.session_store.get(session.sid).uid)

    def test_run_wkhtmltopdf_passes_local_html_and_allow_paths(self):
        html = (
            f'<!DOCTYPE html><html><head><link rel="stylesheet" href="{STATIC_CSS}"/>'
            f"</head><body/></html>"
        )
        captured = {}

        def fake_run(report, bodies, **kwargs):
            captured.update(kwargs, bodies=bodies, context=report.env.context)
            captured["args"] = report._build_wkhtmltopdf_args(
                report.env.ref("base.paperformat_euro"), False
            )
            return b"%PDF"

        with patch.object(
            base_report.IrActionsReport,
            "_run_wkhtmltopdf",
            autospec=True,
            side_effect=fake_run,
        ):
            pdf = self.report._run_wkhtmltopdf([html, html], header=html, footer=None)
        self.assertEqual(pdf, b"%PDF")
        expected = self.localizer().localize_html(html)
        self.assertIn(self.file_url(STATIC_CSS), expected)
        self.assertEqual(captured["bodies"], [expected, expected])
        self.assertEqual(captured["header"], expected)
        self.assertIsNone(captured["footer"])
        allow = captured["context"]["wkhtmltopdf_allow_paths"]
        workdir = next(path for path in allow if "report.assets.tmp." in path)
        self.assertEqual(allow, sorted([workdir, self.static_root]))
        self.assertFalse(os.path.exists(workdir))
        args = captured["args"]
        self.assertIn("--disable-local-file-access", args)
        self.assertEqual(
            [args[i + 1] for i, a in enumerate(args) if a == "--allow"], allow
        )
        self.assertNotIn("--allow", self.report._build_wkhtmltopdf_args(None, False))

    def test_real_wkhtmltopdf_needs_no_http(self):
        try:
            base_report._get_wkhtmltopdf_bin()
        except OSError:
            self.skipTest("wkhtmltopdf not installed")
        popen, captured = subprocess.Popen, {}

        def spy(cmd, *args, **kwargs):
            captured["cmd"] = cmd
            captured["html"] = "".join(
                Path(p).read_text() for p in cmd if p.endswith(".html")
            )
            return popen(cmd, *args, **kwargs)

        module = self.env.ref("base.module_web")
        report = self.report.with_context(force_report_rendering=True)
        with (
            patch.object(base_report.subprocess, "Popen", side_effect=spy),
            self.assertNoLogs(base_report.__name__, logging.WARNING),
        ):
            pdf, _ = report._render_qweb_pdf(
                "base.report_irmodulereference", [module.id]
            )
        self.assertTrue(pdf.startswith(b"%PDF"))
        self.assertIn("--allow", captured["cmd"])
        remote = set(re.findall(r'(?:src|href)="(https?://[^"]+)"', captured["html"]))
        self.assertLessEqual(remote, {self.origin, f"{self.origin}/"})
        self.assertIn('href="file://', captured["html"])
