This module fills in the document indexes (e.g. a Table of Content) in a generated py3o document.

This is to work around the missing feature first reported in 2012: https://bugs.documentfoundation.org/show_bug.cgi?id=44448

It uses the workaround given in https://ask.libreoffice.org/t/update-toc-via-command-line/52518 and other similar threads.

Note that to work, the macro has to be installed in libreoffice first.
This is done at module install.
It assumes the macro files are stored at `~/.config/libreoffice/4/user/basic/Standard`.
If it fails, the function can be manually called with the real path using:
`self.env["py3o.report"]._install_update_index_macro(real_path)`
Make sure that this is correct as most failure paths of the macro application are silent.

Once this is done, py3o templates have an "has index" boolean.
If set, the macro is applied after generation (and before pdf conversion) to update all indices.
