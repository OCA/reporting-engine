# -*- coding: utf-8 -*-
# © 2016 ABF OSIELL <http://osiell.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import itertools
import traceback
import logging

from openerp import api, fields, models, registry, SUPERUSER_ID
from openerp.exceptions import Warning as UserError
from openerp.tools.translate import _
from openerp.tools.safe_eval import safe_eval

from openerp.addons.connector.event import Event
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession

_logger = logging.getLogger(__name__)

on_action_run = Event()


class MassReport(models.Model):
    _name = 'mass.report'
    _inherit = ['mail.thread']
    _description = u"Mass report"
    _track = {
        'state': {
            'mass_reporting.mt_mass_report_done':
            lambda self, cr, uid, obj, ctx=None: obj.state == 'done',
        },
    }

    name = fields.Char(
        u"Name", required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    state = fields.Selection(
        [('draft', u"Draft"),
         ('working', u"Working"),
         ('ready', u"Ready"),
         ('done', u"Done"),
         ('failed', u"Failed"),
         ],
        string=u"Status", readonly=True, default='draft',
        track_visibility='onchange')
    model_id = fields.Many2one(
        'ir.model', string=u"Model",
        required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    model = fields.Char(u"Model", related='model_id.model')
    user_id = fields.Many2one(
        'res.users', string=u"Run as", readonly=True,
        states={'draft': [('readonly', False)]},
        default=lambda obj: obj.env.user.id)
    line_ids = fields.One2many(
        'mass.report.line', 'mass_report_id',
        string="Reports", copy=True, readonly=True,
        states={'draft': [('readonly', False)]})
    filter_ids = fields.Many2many(
        'ir.filters',
        'mass_report_filter_rel',
        'mass_report_id', 'filter_id',
        string=u"Filters", readonly=True,
        states={'draft': [('readonly', False)]},
        domain="[('model_id', '=', model), ('domain', '!=', '[]')]")
    output_format = fields.Many2one(
        'ir.model',
        domain=[('model', '=like', 'mass.report.output.%')],
        string=u"Output format", required=True, readonly=True,
        states={'draft': [('readonly', False)]})
    run_build_manually = fields.Boolean(
        u"Build manually", readonly=True,
        states={'draft': [('readonly', False)]},
        help=(u"If checked, the mass report will wait for your approval "
              u"to be built."))
    output_file = fields.Many2one(
        'ir.attachment', string=u"File", copy=False, readonly=True)
    report_attachment_ids = fields.One2many(
        'mass.report.attachment', 'mass_report_id',
        string=u"Lines", readonly=True,
        states={'draft': [('readonly', False)]})

    @api.multi
    def check_report_types(self):
        """Check if the output format is compatible
        with the selected reports.
        """
        for mr in self:
            output_format = self.env[mr.output_format.model]
            report_type_combinations = output_format.get_report_types()
            if not report_type_combinations:
                return True
            selected_report_types = tuple(sorted(set([
                line.report_id.report_type for line in mr.line_ids])))
            report_types_perm = []
            for report_types in report_type_combinations:
                for length in range(0, len(report_types) + 1):
                    for subset in itertools.permutations(report_types, length):
                        report_types_perm.append(subset)
            if selected_report_types not in report_types_perm:
                report_types_available = [
                    ', '.join(report_types)
                    for report_types in report_type_combinations]
                raise UserError(
                    _(u"The selected output format only supports the "
                      u"following report types:\n"
                      u"%s") % '\nor '.join(report_types_available))
        return True

    @api.multi
    def action_prepare(self):
        """Prepare the list of reports to process."""
        report_attachment_model = self.env['mass.report.attachment']
        for mr in self:
            mr.check_report_types()
            domain = self._generate_domain()
            records = self._get_records(mr.model_id, domain)
            mr.report_attachment_ids.unlink()   # Reset before generate
            for record in records:
                for line in mr.line_ids:
                    vals = {
                        'mass_report_id': mr.id,
                        'mass_report_line_id': line.id,
                        'record_id': '%s,%s' % (record._name, record.id),
                    }
                    report_attachment_model.create(vals)
        return True

    @api.multi
    def action_draft(self):
        for mr in self:
            mr.state = 'draft'
            mr.report_attachment_ids.unlink()
            mr.output_file.unlink()
        return True

    @api.multi
    def action_run(self):
        """Create the jobs to generate reports."""
        session = ConnectorSession(
            self.env.cr, self.env.uid, context=self.env.context)
        for mr in self:
            mr.message_subscribe_users(mr.user_id.id)
            if not mr.report_attachment_ids:
                mr.action_prepare()
            on_action_run.fire(session, mr._name, mr.id)
            mr.state = 'working'
        return True

    @api.model
    def check_build(self):
        """Run by cron, check if there are mass reports ready to be built."""
        mrs = self.search([('state', '=', 'working')])
        for mr in mrs:
            job_states = mr.report_attachment_ids.mapped('queue_job_state')
            if all(state == 'done' for state in job_states):
                mr.state = 'ready'
                if not mr.run_build_manually:
                    mr.action_build()
            elif (all(state in ['done', 'failed'] for state in job_states)
                  and any(state == 'failed' for state in job_states)):
                mr.state = 'failed'
        return True

    @api.multi
    def action_build(self):
        """Build the mass report."""
        for mr in self:
            output_format = self.env[mr.output_format.model]
            try:
                output_format.process_mass_report(mr.id)
            except:
                tb = traceback.format_exc()
                _logger.error(tb)
                mr.state = 'failed'
                mr.message_post(tb, content_subtype='plaintext')
            else:
                mr.state = 'done'
        return True

    @api.multi
    def _generate_domain(self):
        self.ensure_one()
        domain = []
        for filter_ in self.filter_ids:
            domain.extend(safe_eval(filter_.domain))
        return domain

    @api.model
    def _get_records(self, model, domain=None):
        if domain is None:
            domain = []
        record_model = self.env[model.model]
        return record_model.search(domain)


@on_action_run
def delay_main_job(session, model, record_id):
    run_main_job.delay(session, model, record_id)


@job
def run_main_job(session, model, record_id):
    mass_report_model = session.env[model]
    mr = mass_report_model.browse(record_id)
    for ra in mr.report_attachment_ids:
        create_attachment.delay(session, ra._name, ra.id)


@job
def create_attachment(session, model, record_id):
    ra_model = session.env[model]
    ra = ra_model.browse(record_id)
    attach_job_to_record(session, ra._name, ra.id, 'queue_job_id')
    output_format = session.env[ra.mass_report_id.output_format.model]
    output_format._process_report_attachment(ra)


def attach_job_to_record(session, model_name, record_id, m2o_field):
    if not session.context.get('job_uuid'):
        return
    job_uuid = session.context['job_uuid']
    with api.Environment.manage():
        with registry(session.env.cr.dbname).cursor() as new_cr:
            new_env = api.Environment(
                new_cr, SUPERUSER_ID, session.env.context)
            record = new_env[model_name].browse(record_id)
            job_model = new_env['queue.job']
            jobs = job_model.search([('uuid', '=', job_uuid)])
            if jobs:
                setattr(record, m2o_field, jobs[0])
            new_env.cr.commit()
