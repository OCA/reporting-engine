# Copyright 2019 Ecosoft Co., Ltd (http://ecosoft.co.th/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html)
from odoo.tests import common
from odoo.tests.common import Form
from odoo.exceptions import UserError


class TestJobChannel(common.TransactionCase):

    def setUp(self):
        super(TestJobChannel, self).setUp()
        self.print_doc = self.env.ref('report_async.'
                                      'report_async_print_document')
        self.test_rec = self.env.ref('base.module_mail')
        self.test_rpt = self.env.ref('base.ir_module_reference_print')

    def _print_wizard(self, res):
        obj = self.env[res['res_model']]
        ctx = {'active_model': self.print_doc._name,
               'active_id': self.print_doc.id, }
        ctx.update(res['context'])
        with Form(obj.with_context(ctx)) as form:
            form.reference = '%s,%s' % (self.test_rec._name, self.test_rec.id)
            form.action_report_id = self.test_rpt
        print_wizard = form.save()
        return print_wizard

    def test_1_run_now(self):
        """Run now will return report action as normal"""
        res = self.print_doc.run_now()
        report_action = self._print_wizard(res).print_report()
        self.assertEquals(report_action['type'], 'ir.actions.report')

    def test_2_run_async(self):
        """Run background will return nothing, job started"""
        with self.assertRaises(UserError):
            self.print_doc.run_async()
        self.print_doc.write({'allow_async': True,
                              'email_notify': True})
        res = self.print_doc.run_async()
        print_wizard = self._print_wizard(res)
        report_action = print_wizard.print_report()
        self.assertEquals(report_action, {})  # Do not run report yet
        self.assertEquals(self.print_doc.job_status, 'pending')  # Job started
        # Test produce file (as queue will not run in test mode)
        docids = [print_wizard.reference.id]
        data = None
        report_id = self.test_rpt.id
        user_id = self.env.user.id
        self.print_doc.run_report(docids, data, report_id, user_id)
        # Check name of the newly producted file
        # Note: on env with test-enable, always fall back to render_qweb_html
        self.assertIn(self.test_rpt.name, self.print_doc.file_ids[0].name)
        # View fileds/jobs
        self.print_doc.view_files()
        self.print_doc.view_jobs()
