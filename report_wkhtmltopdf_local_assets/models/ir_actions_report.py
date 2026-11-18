# Copyright 2026 Pop Solutions
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import hashlib
import logging
import mimetypes
import os
import re
import shutil
import tempfile
import threading
from pathlib import Path
from urllib.parse import urljoin, urlsplit

import lxml.html
from werkzeug.test import Client

from odoo import api, models
from odoo.http import request, root
from odoo.service import security

_logger = logging.getLogger(__name__)

CSS_URL_RE = re.compile(r"""url\(\s*(?P<q>['"]?)(?P<url>[^'"()\s]+)(?P=q)\s*\)""")
DOCTYPE_RE = re.compile(r"\s*<!DOCTYPE[^>]*>", re.IGNORECASE)
EXTENSIONS = {"text/javascript": ".js", "application/javascript": ".js"}
THREAD_ATTRS = (
    "dbname",
    "uid",
    "url",
    "query_count",
    "query_time",
    "perf_t0",
    "cursor_mode",
)


class AssetLocalizer:
    """Rewrite the URLs of a report HTML so wkhtmltopdf reads local files.

    Static files are referenced in place. Anything else served by this
    Odoo instance is fetched in-process, without going through the HTTP
    workers, and written to ``workdir``. URLs that cannot be resolved are
    left untouched.
    """

    def __init__(self, env, workdir, session_id=None):
        self.env = env
        self.workdir = workdir
        self.session_id = session_id
        self.cache = {}
        self.allow_paths = set()
        get_param = env["ir.config_parameter"].sudo().get_param
        self.origin = env["ir.actions.report"]._get_report_url()
        self.hosts = {
            urlsplit(url).netloc for url in (self.origin, get_param("web.base.url", ""))
        } - {""}

    def localize_html(self, html):
        if not html:
            return html
        doctype = DOCTYPE_RE.match(html)
        doc = lxml.html.document_fromstring(html)
        base = doc.find(".//base")
        base_url = base.get("href") if base is not None else self.origin
        for node in doc.iter("link", "script", "img"):
            attr = "href" if node.tag == "link" else "src"
            if node.tag == "link" and "stylesheet" not in (node.get("rel") or ""):
                continue
            local = self.localize_url(node.get(attr), base_url)
            if local:
                node.set(attr, local)
        for node in doc.xpath("//*[@style]"):
            node.set("style", self.localize_css(node.get("style"), base_url))
        for node in doc.iter("style"):
            if node.text:
                node.text = self.localize_css(node.text, base_url)
        result = lxml.html.tostring(doc, encoding="unicode")
        return doctype.group(0) + result if doctype else result

    def localize_css(self, css, base_url, static_only=False):
        def replace(match):
            local = self.localize_url(match.group("url"), base_url, static_only)
            return f"url({local})" if local else match.group(0)

        return CSS_URL_RE.sub(replace, css)

    def localize_url(self, url, base_url, static_only=False):
        """Return a ``file://`` URL for ``url`` or None to leave it untouched.

        With ``static_only`` (references inside stylesheets, most of which the
        page never uses), only files that can be read from disk are rewritten.
        """
        if not url or url.startswith("#"):
            return None
        parts = urlsplit(urljoin(base_url, url.strip()))
        if parts.scheme not in ("http", "https") or parts.netloc not in self.hosts:
            return None
        static_path = root.get_static_file(parts.path)
        if static_path:
            static_root, _, _ = static_path.rpartition(f"{os.sep}static{os.sep}")
            self.allow_paths.add(f"{static_root}{os.sep}static")
            return Path(static_path).as_uri()
        if static_only:
            return None
        key = parts.path + (f"?{parts.query}" if parts.query else "")
        if key not in self.cache:
            self.cache[key] = None  # break cycles
            self.cache[key] = self._fetch_to_workdir(parts.path, key)
        return self.cache[key]

    def _fetch_to_workdir(self, path, key):
        fetched = self._fetch(key)
        if not fetched:
            return None
        mimetype, data = fetched
        if mimetype == "text/css":
            css = self.localize_css(
                data.decode(errors="replace"), urljoin(self.origin, path), True
            )
            data = css.encode()
        name = hashlib.sha1(key.encode()).hexdigest()
        extension = (
            EXTENSIONS.get(mimetype) or mimetypes.guess_extension(mimetype) or ""
        )
        local_path = os.path.join(self.workdir, name + extension)
        with open(local_path, "wb") as local_file:
            local_file.write(data)
        return Path(local_path).as_uri()

    def _fetch(self, key):
        headers = {"Cookie": f"session_id={self.session_id}"} if self.session_id else {}
        thread = threading.current_thread()
        saved = {
            attr: getattr(thread, attr)
            for attr in THREAD_ATTRS
            if hasattr(thread, attr)
        }
        try:
            response = Client(root, use_cookies=False).get(
                key,
                base_url=self.origin,
                headers=headers,
                environ_base={"REMOTE_ADDR": "127.0.0.1"},
            )
            try:
                if response.status_code != 200 or "X-Sendfile" in response.headers:
                    return None
                return response.mimetype, response.get_data()
            finally:
                response.close()
        except Exception:
            _logger.warning("Could not fetch report asset %s", key, exc_info=True)
            return None
        finally:
            for attr in THREAD_ATTRS:
                if hasattr(thread, attr):
                    delattr(thread, attr)
            for attr, value in saved.items():
                setattr(thread, attr, value)


class IrActionsReport(models.Model):
    _inherit = "ir.actions.report"

    @api.model
    def _build_wkhtmltopdf_args(
        self,
        paperformat_id,
        landscape,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        args = super()._build_wkhtmltopdf_args(
            paperformat_id,
            landscape,
            specific_paperformat_args=specific_paperformat_args,
            set_viewport_size=set_viewport_size,
        )
        for path in self.env.context.get("wkhtmltopdf_allow_paths", ()):
            args.extend(["--allow", path])
        return args

    @api.model
    def _run_wkhtmltopdf(
        self,
        bodies,
        report_ref=False,
        header=None,
        footer=None,
        landscape=False,
        specific_paperformat_args=None,
        set_viewport_size=False,
    ):
        workdir = tempfile.mkdtemp(prefix="report.assets.tmp.")
        session = self._wkhtmltopdf_asset_session()
        try:
            localizer = AssetLocalizer(self.env, workdir, session and session.sid)
            bodies = [localizer.localize_html(body) for body in bodies]
            header = localizer.localize_html(header)
            footer = localizer.localize_html(footer)
            allow_paths = sorted(localizer.allow_paths | {workdir})
            report = self.with_context(wkhtmltopdf_allow_paths=allow_paths)
            return super(IrActionsReport, report)._run_wkhtmltopdf(
                bodies,
                report_ref=report_ref,
                header=header,
                footer=footer,
                landscape=landscape,
                specific_paperformat_args=specific_paperformat_args,
                set_viewport_size=set_viewport_size,
            )
        finally:
            if session:
                root.session_store.delete(session)
            shutil.rmtree(workdir, ignore_errors=True)

    @api.model
    def _wkhtmltopdf_asset_session(self):
        """Temporary copy of the user session, as the core does for the cookie
        jar, so in-process asset requests run with the same access rights."""
        if not (request and request.db):
            return None
        session = root.session_store.new()
        session.update({**request.session, "debug": "", "_trace_disable": True})
        if session.uid:
            session.session_token = security.compute_session_token(session, self.env)
        root.session_store.save(session)
        return session
