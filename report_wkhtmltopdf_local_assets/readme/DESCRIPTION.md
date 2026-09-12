wkhtmltopdf fetches the stylesheets, scripts, fonts and images of a report
over HTTP from the Odoo server that spawned it. Every one of those requests
needs a free HTTP worker: once all workers are busy rendering PDFs, the
requests queue behind them, wkhtmltopdf waits for its network timeout and
the whole instance stops answering
([odoo/odoo#199880](https://github.com/odoo/odoo/issues/199880)).

This module removes the round-trip. Before calling wkhtmltopdf, the report
HTML is rewritten so that:

- static files (`/<module>/static/...`) are read straight from disk;
- everything else served by this instance (asset bundles, `/web/image`,
  barcodes, ...) is resolved in-process and written to a temporary
  directory;
- inside stylesheets, `url()` references to static files are rewritten as
  well; dynamic ones are left alone, since most of them are never used by
  the page.

wkhtmltopdf keeps running with `--disable-local-file-access`; only the
directories involved are passed with `--allow`. URLs that cannot be
resolved are left untouched, so the behaviour never gets worse than
without the module.
