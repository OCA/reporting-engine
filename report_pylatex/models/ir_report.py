# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2024 OmniaSolutions (<http://omniasolutions.website>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import re
import tempfile
import logging
import base64
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import xml.etree.cElementTree as ElementTree
from collections import OrderedDict
from ast import literal_eval

import pylatex
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape

template_report = """
def generate_unique(self, record_id, data):
    import pylatex
    geometry_options = {
        "head": "40pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True
    }
    
    doc = pylatex.Document(geometry_options=geometry_options)
    #
    # Configure heder
    #
    first_page = pylatex.PageStyle("firstpage")
    #
    # Header image
    #
    with first_page.create(pylatex.Head("L")) as header_left:
        with header_left.create(pylatex.MiniPage(width=pylatex.utils.NoEscape(r"0.49\textwidth"),
                                         pos='c')) as title_wrapper:
            title_wrapper.append(pylatex.SmallText(pylatex.utils.bold(f"{record_id.company_id.name} • {record_id.company_id.street} • {record_id.company_id.zip} {record_id.company_id.city}")))                             
                                           

    # Add document title
    with first_page.create(pylatex.Head("R")) as right_header:
        with right_header.create(pylatex.MiniPage(width=NoEscape(r"0.49\textwidth"),
                                 pos='c', align='r')) as title_wrapper:
            logo_file = self.getImagePathFromContent(record_id.company_id.logo)
            title_wrapper.append(pylatex.StandAloneGraphic(image_options="width=120px",
                               filename=logo_file))
            title_wrapper.append("\n")
            title_wrapper.append(pylatex.LargeText(pylatex.utils.bold(record_id.partner_id.display_name)))
            title_wrapper.append(pylatex.LineBreak())
            title_wrapper.append(pylatex.MediumText(pylatex.utils.bold(record_id.date_order)))
    
    doc.preamble.append(first_page)
    #
    #Add customer information
    with doc.create(pylatex.Tabu("X[l] X[r]")) as first_page_table:
        customer = pylatex.MiniPage(width=NoEscape(r"0.49\textwidth"), pos='h')
        customer.append("Verna Volcano")
        customer.append("\n")
        customer.append("For some Person")
        customer.append("\n")
        customer.append("Address1")
        customer.append("\n")
        customer.append("Address2")
        customer.append("\n")
        customer.append("Address3")

        # Add branch information
        branch = pylatex.MiniPage(width=NoEscape(r"0.49\textwidth"), pos='t!',
                          align='r')
        branch.append("Branch no.")
        branch.append(pylatex.LineBreak())
        branch.append(pylatex.utils.bold("1181..."))
        branch.append(pylatex.LineBreak())
        branch.append(pylatex.utils.bold("TIB Cheque"))

        first_page_table.add_row([customer, branch])
        first_page_table.add_empty_row()
    
    # Add footer
    with first_page.create(pylatex.Foot("C")) as footer:
        message = "Important message please read"
        with footer.create(pylatex.Tabularx(
                "X X X X",
                width_argument=pylatex.utils.NoEscape(r"\textwidth"))) as footer_table:

            footer_table.add_row(
                [pylatex.MultiColumn(4, align='l', data=pylatex.TextColor("blue", message))])
            footer_table.add_hline(color="blue")
            footer_table.add_empty_row()

            branch_address = pylatex.MiniPage(
                width=NoEscape(r"0.25\textwidth"),
                pos='t')
            branch_address.append("960 - 22nd street east")
            branch_address.append("\n")
            branch_address.append("Saskatoon, SK")

            document_details = pylatex.MiniPage(width=pylatex.utils.NoEscape(r"0.25\textwidth"),
                                        pos='t', align='r')
            document_details.append("1000")
            document_details.append(pylatex.LineBreak())
            document_details.append(pylatex.simple_page_number())

            footer_table.add_row([branch_address, branch_address,
                                  branch_address, document_details])
    doc.change_document_style("firstpage")
    
    #
    # Add statement table
    #
    with doc.create(pylatex.LongTabu("X[l] X[2l] X[r] X[r] X[r] X[r]",
                             row_height=1.5)) as data_table:
        data_table.add_row(["Position",
                            "Name",
                            "Description",
                            "Qty",
                            "UnitPrice",
                            "RawPrice"],
                           mapper=pylatex.utils.bold,
                           color="lightgray")
        data_table.add_empty_row()
        data_table.add_hline()
        for i, sale_order_line in enumerate(record_id.order_line):
            row = [sale_order_line.sequence,
                   sale_order_line.product_id.display_name,
                   sale_order_line.name,
                   sale_order_line.product_uom_qty,
                   sale_order_line.price_unit,
                   sale_order_line.price_subtotal
                   ]
            if (i % 2) == 0:
                data_table.add_row(row, color="lightgray")
            else:
                data_table.add_row(row)
    #
    return doc
"""

class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("pylatex", "PyLatex"),
                       ], ondelete={"pylatex": "set default"}
    )
    
    report_code = fields.Text('Report Code',
                              default=template_report)

    @api.model
    def _get_report_from_name(self, report_name):
        report_obj = self.env["ir.actions.report"]
        qwebtypes = ["pylatex"]
        filter_type = self.env.context.get('report_type', qwebtypes)
        if not isinstance(filter_type, list):
            filter_type= [filter_type]
        conditions = [
            ("report_type", "in",filter_type ),
            ("report_name", "=", report_name),
        ]
        context = self.env["res.users"].context_get()
        ret = report_obj.with_context(context).search(conditions, limit=1)
        if not ret:
            ret = super(ReportAction, self)._get_report_from_name(report_name)
        return ret

    def _render_pylatex(self,
                        res_ids=None,
                        data=None):
        self_sudo = self.sudo()
        model = self.env[self_sudo.model]
        record_ids = model
        if not data:
            data = {}
        save_in_attachment = OrderedDict()
        if res_ids:
            record_ids = model.browse(res_ids)
            wk_record_ids = model
            if self_sudo.attachment:
                for record_id in record_ids:
                    attachment = self_sudo.retrieve_attachment(record_id)
                    if attachment:
                        save_in_attachment[record_id.id] = self_sudo._retrieve_stream_from_attachment(attachment)
                    if not self_sudo.attachment_use or not attachment:
                        wk_record_ids += record_id
            else:
                wk_record_ids = record_ids
            res_ids = wk_record_ids.ids
        if save_in_attachment and not res_ids:
            logging.info('The PDF report has been generated from attachments.')
            self_sudo._post_pdf(save_in_attachment)
            return save_in_attachment
        for record_id in record_ids:
            pdf_content = self._get_pylatex_pdf(record_id, data)
            #
            # TODO Use Pypdf2 to merge the file
            #
            # aggiungere gli allegati mergiati
            #
            break
        return pdf_content,'pdf'

    def _get_pylatex_pdf(self, record_id, data):
        #
        # Document with `\maketitle` command activated
        #
        exec(self.report_code)
        #
        doc = locals()['generate_unique'](self, record_id, data) 
        #
        pdf_file = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
        doc.generate_pdf(filepath=pdf_file, clean_tex=False)
        documentContent = None
        with open(f"{pdf_file}.pdf",'rb') as f:
            documentContent = f.read()
        try:
            os.unlink(f"{pdf_file}.pdf")
        except Exception as ex:
            logging.error(ex)
        return documentContent   
    
    def getImagePathFromContent(self, content):
        img_file = os.path.join(tempfile._get_default_tempdir(), next(tempfile._get_candidate_names()))
        img_file = f"{img_file}.png"
        with open(img_file, 'wb') as f:
            f.write(base64.b64decode(content))
        return img_file
        
    def getEmptyIfNot(self, record, field_name):
        value = getattr(record, field_name)
        if value:
            return value
        return ''
        
    def get_partner_address_minipage(self, partner_id, fields=[]):
        minipage = pylatex.MiniPage()
        if 'name' in fields or not fields:
            minipage.append(f"{partner_id.name}")
            minipage.append("\n")
        if 'street' in fields or not fields:
            minipage.append(f"{partner_id.street}")
            minipage.append("\n")
        if 'zip' in fields or not fields:
            minipage.append(f"{partner_id.zip} {partner_id.city}")
            minipage.append("\n")
        if 'state' in fields or not fields:
            minipage.append(f"{partner_id.state_id.display_name}")
            minipage.append("\n")
        if 'country' in fields or not fields:
            minipage.append(f"{partner_id.country_id.display_name}")
        return minipage
        
        