Glue module for BI View Editor and Spreadsheet Dashboard.

To avoid a dependency of the ``bi_view_editor`` module on the ``spreadsheet``
module through the ``spreadsheet_dashboard`` module, the ``bi_view_editor``
menu items are parented to the legacy ``base.menu_board_root`` menu. In case
the ``spreadsheet_dashboard`` module is installed, this auto-installable
module moves them to the ``spreadsheet_dashboard`` menu.
