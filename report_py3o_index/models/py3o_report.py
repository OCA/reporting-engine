# Copyright 2024 fah-mili/Lambdao
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


import logging
import os
import subprocess
import pkg_resources

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"

    py3o_has_index = fields.Boolean(
        "Has Py3o Index?",
        default=False,
        compute='_compute_py3o_has_index',
        help="Check if the template has a py3o index. "
             "It needs to be compiled twice to get the index right."
    )

    @api.depends(
        'ir_actions_report_id.py3o_template_id.py3o_has_index',
        'ir_actions_report_id.py3o_has_index_fallback'
    )
    def _compute_py3o_has_index(self):
        for rec in self:
            if rec.ir_actions_report_id.py3o_template_id:
                value = rec.ir_actions_report_id.py3o_template_id.py3o_has_index
            else:
                value = rec.ir_actions_report_id.py3o_has_index_fallback
            rec.py3o_has_index = value

    @api.model
    def _install_update_index_macro(self, path=None):
        """ Install or update the py3o index macro
        """
        # the real path is an argument so that in case it fails it can be
        # called again with the correct one; after that it's LO's internal
        # macro naming that will be used
        # we could also have a parameter for the macro name but
        # is it worth the complexity?
        if not path:
            path = "~/.config/libreoffice/4/user/basic/Standard"
        real_path = os.path.realpath(os.path.expanduser(path))
        file_macro = "ModuleUpdateIndex.xba"
        macro_path = os.path.join(real_path, file_macro)
        if not os.path.exists(macro_path):
            # copy the new macro to libreoffice macro folder
            content_path = pkg_resources.resource_filename(
                'odoo.addons.report_py3o_index',
                'data/ModuleUpdateIndex.xba'
            )
            with open(content_path, 'r') as f:
                content = f.read()
            with open(macro_path, 'w') as f:
                f.write(content)
            file_script = "script.xlb"
            script_path = os.path.join(real_path, file_script)
            mac = '<library:element library:name="ModuleUpdateIndex"/>'
            with open(script_path, 'r') as f:
                script_content = f.read()
            if mac not in script_content:
                end_marker = '</library:library>'
                marker_line = mac + "\n" + end_marker
                new_content = script_content.replace(end_marker, marker_line)
                with open(script_path, 'w') as f:
                    f.write(new_content)

    @api.multi
    def _convert_single_report(self, result_path, model_instance, data):
        # this needs to be done before the report is converted to pdf!
        # data is an unused dict, the file is obtained from the result_path
        if self.py3o_has_index:
            self._update_index(result_path)
        result = super(Py3oReport, self)._convert_single_report(
            result_path, model_instance, data
        )
        return result

    def _update_index(self, result_path):
        """Run a command to update the index"""
        path = "macro:///Standard.ModuleUpdateIndex.UpdateIndexes(%s)" % result_path
        lo_bin = self.ir_actions_report_id.lo_bin_path
        cmd = [lo_bin, '--headless', path]
        # if something goes wrong, it's not giving any error message...
        subprocess.check_output(cmd, cwd=os.path.dirname(result_path))
        return result_path
