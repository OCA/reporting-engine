# Copyright 2015 ACSONE SA/NV (<http://acsone.eu>)
# Copyright 2024 OmniaSolutions (<http://omniasolutions.website>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl.html).
import os
import re
import time
import base64
import logging
import tempfile
import lxml.html
from odoo import _, api, fields, models
from odoo.exceptions import UserError
import xml.etree.cElementTree as ElementTree
from collections import OrderedDict
from ast import literal_eval
import more_itertools as mit
import pylatex
from pylatex import Document, Section, Subsection, Command
from pylatex.utils import italic, NoEscape
from .utils import Html2Latex

template_report = r"""
def generate_unique(self, record_id, data):
    import pylatex
    geometry_options = {
        "head": "40pt",
        "margin": "0.5in",
        "bottom": "0.6in",
        "includeheadfoot": True
    }
    
    doc = pylatex.Document(geometry_options=geometry_options)
    doc.preamble.append(pylatex.Command('usepackage', 'helvet'))
    doc.packages.append(pylatex.Package('color'))
    doc.packages.append(pylatex.Package('colortbl'))
    doc.add_color(name="lightgray", model="gray", description="0.80")
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
            title_wrapper.append(pylatex.utils.NoEscape(f"\\tiny { record_id.company_id.name} • {record_id.company_id.street} • {record_id.company_id.zip} {record_id.company_id.city}"))
                                           

    # Add document title
    with first_page.create(pylatex.Head("R")) as right_header:
        with right_header.create(pylatex.MiniPage(width=NoEscape(r"0.49\textwidth"),
                                 pos='c', align='r')) as title_wrapper:
            img = self.StandAloneGraphic(record_id.company_id.logo,
                                         image_options="width=200px")
            title_wrapper.append(img)

    
    doc.preamble.append(first_page)

    #
    # Add customer information
    #
    with doc.create(pylatex.Tabu("X[l] X[r]")) as first_page_table:
        customer = pylatex.MiniPage(width=NoEscape(r"0.49\textwidth"), pos='h')
        customer.append(f"{record_id.partner_id.name}")
        customer.append(f"{record_id.partner_id.street}")
        customer.append(f"{record_id.partner_id.zip} {record_id.partner_id.city}")
        customer.append(f"{record_id.partner_id.state_id.display_name}")
        customer.append(f"{record_id.partner_id.country_id.display_name}")
        


        # Add branch information
        right_branch = pylatex.MiniPage(width=NoEscape(r"0.49\textwidth"), pos='t!',
                          align='r')
        if record_id.state in ['draft']:
          right_branch.append(pylatex.LargeText(pylatex.utils.bold('Quotation')))
        if record_id.state in ['sale']:
          right_branch.append(pylatex.LargeText(pylatex.utils.bold('Order')))
        right_branch.append(pylatex.LineBreak())
        #
        right_branch.append(pylatex.LineBreak())
        #
        sub_table = pylatex.Tabu("X[r] X[l]")
        sub_table.add_row([pylatex.utils.bold(f"Offer number:"),
                           pylatex.utils.bold(f"{record_id.name}")])
        if record_id.analytic_account_id:
            sub_table.add_row([pylatex.utils.bold(f"Project number:"),
                               pylatex.utils.bold(f"{record_id.analytic_account_id.name if record_id.analytic_account_id else ''}")])
        sub_table.add_row([pylatex.utils.bold(f"Date:"),
                           pylatex.utils.bold(f"{record_id.date_order}")])
        sub_table.add_row([pylatex.utils.bold(f"Valid until:"),
                           pylatex.utils.bold(f"{record_id.validity_date}")])
        sub_table.add_row([pylatex.utils.bold(f"Attn:"),
                   pylatex.utils.bold(f"{record_id.validity_date}")])
        sub_table.add_row([pylatex.utils.bold(f"Contact person:"),
                   pylatex.utils.bold(f"{record_id.user_id.name}")])
        sub_table.add_row([pylatex.utils.bold(f"Telephone:"),
                   pylatex.utils.bold(f"+49 6359 9477 410")])
        sub_table.add_row([pylatex.utils.bold(f"Email:"),
                   pylatex.utils.bold(f"{record_id.user_id.partner_id.email}")])
        right_branch.append(sub_table)
        first_page_table.add_row([customer, right_branch])
        first_page_table.add_empty_row()

    #
    # Add footer
    #
    with first_page.create(pylatex.Foot("C")) as footer:
        with footer.create(pylatex.Tabularx("X X   X",
                                            width_argument=pylatex.utils.NoEscape(r"\textwidth"))) as footer_table:

            branch_address = pylatex.MiniPage(width=NoEscape(r"0.2\textwidth"),
                                              pos='c')
            branch_address.append(pylatex.utils.NoEscape(f"\\tiny " + self.gEINot(record_id.company_id,'name')))
            branch_address.append(pylatex.utils.NoEscape(f"\\tiny "+ self.gEINot(record_id.company_id,'street')))

            branch_bank = pylatex.MiniPage(width=NoEscape(r"0.2\textwidth"),
                                           pos='c')
            
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny Bank details:"))
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny Demo Bank"))
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny IBAN: <>"))
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny BIC: <>"))
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny <>"))
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny IBAN: <>"))
            branch_bank.append(pylatex.utils.NoEscape(f"\\tiny BIC: <>"))
            branch_bank.append(pylatex.utils.bold(pylatex.simple_page_number()))
            
            branch_head = pylatex.MiniPage(width=NoEscape(r"0.2\textwidth"),
                                  pos='c')
            
            branch_head.append(pylatex.utils.NoEscape(f"\\tiny Executive board:"))
            branch_head.append(pylatex.utils.NoEscape(f"\\tiny <>"))
            branch_head.append(pylatex.utils.NoEscape(f"\\tiny <>"))
            branch_head.append(pylatex.utils.NoEscape(f"\\tiny Register court: <>"))
            branch_head.append(pylatex.utils.NoEscape(f"\\tiny Register no.: <>"))
            branch_head.append(pylatex.utils.NoEscape(f"\\tiny VAT ID no.: <>"))



            footer_table.add_row([branch_address,
                                  branch_bank,
                                  branch_head])

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
            if sale_order_line.display_type =='line_section':
                row = [sale_order_line.name,
                     ""
                     "",
                     "",
                     "",
                     ""
                     ]
            elif sale_order_line.display_type =='line_note':
                row = [sale_order_line.name,
                     ""
                     "",
                     "",
                     "",
                     ""
                     ]
            else:
                row = [i,
                     sale_order_line.product_id.display_name,
                     sale_order_line.name,
                     sale_order_line.product_uom_qty,
                     sale_order_line.price_unit,
                     sale_order_line.price_subtotal
                     ]
            data_table.add_row(row)
    #
    return doc
"""

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
        
class ReportAction(models.Model):
    _inherit = "ir.actions.report"

    report_type = fields.Selection(
        selection_add=[("pylatex", "PyLatex"),
                       ], ondelete={"pylatex": "set default"}
    )
    
    report_code = fields.Text('Report Code',
                              default=template_report)
    pylatex_debug = fields.Boolean("PyLate Debug",
                                   help="""
                                   if set to true all the file generate by PyLatex will remain in the /tmp folder
                                   for debuggin
                                   """)
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
        pdf_file = self.tmpFolderName
        try:
            doc.generate_pdf(filepath=pdf_file, clean_tex=False)
        except Exception as ex:
            logging.error(ex)
            time.sleep(1)
            if os.path.exists(pdf_file):
                raise ex
        documentContent = None
        with open(f"{pdf_file}.pdf",'rb') as f:
            documentContent = f.read()
        try:
            os.unlink(f"{pdf_file}.pdf")
        except Exception as ex:
            logging.error(ex)
        return documentContent   
    
    @property
    def tmpFolderName(self):
        """
        get session temporary folder
        :return: temporary folder name 
        """
        tmp_folder = self.env.context.get('pylatex_tmp_folder')
        if not tmp_folder:
            tmp_folder = tempfile._get_default_tempdir()
        return os.path.join(tmp_folder , next(tempfile._get_candidate_names()))
    
    def getTempImageName(self, exte="png"):
        return f"{self.tmpFolderName}.{exte}"
        
    def getImagePathFromContent(self, field_content):
        """
        get file path from odoo bynary field image
        :field_content field content in base64.Encode form
        :ret
        """
        return self.getPathFromContent(field_content,'png')

    def getPathFromContent(self, field_content, exte):
        """
        get file path from odoo bynary field
        :field_content field content in base64.Encode form
        :return: fiel path 
        """
        img_file = f"{self.tmpFolderName}.{exte}"
        with open(img_file, 'wb') as f:
            f.write(base64.b64decode(field_content))
        return img_file
    
    def StandAloneGraphic(self,
                          field_content,
                          **args):
        """
        get pyLatex.StandAloneGraphic object from odoo field 
        :field_content field content in base64.Encode form
        :args StandAloneGraphic supported args
        :return: file path of the content
        """
        args['filename'] = self.getImagePathFromContent(field_content)
        return pylatex.StandAloneGraphic(**args)

    def gEINot(self, recordset, field_name):
        """
        Get an empty string if the field is False 
        :recordset odoo recordset
        :field_name field name , also dotted field are computed sale_order.partner_id.name
        """
        value = self.odooGetattr(recordset, field_name)
        if value:
            return value
        return ''

    def odooGetattr(self,
                    recordset,
                    field_name):
        """
        get the odoo field attribute value
        :recordset odoo recordset
        :field_name field name , also dotted field are computed sale_order.partner_id.name
        :return: value
        """
        res = recordset
        for filed_attribute_name in field_name.split("."):
            res = getattr(res,filed_attribute_name)
        return res
    
    def html2Latex(self,
                   pyLtexObject,
                   recordset,
                   field_name):
        html_content = self.odooGetattr(recordset, field_name)
        node = lxml.html.fromstring(html_content)
        pyLtexObject.append(NoEscape('\\begingroup'))
        HtL = Html2Latex(report=self)
        pyLtexObject.append(NoEscape(HtL.element2latex(node)))
        pyLtexObject.append(NoEscape('\\endgroup'))
        
    def add_row(self,
            pyLtexTable,
            content=[],
            content_flavor=[],
            chunks=50,
            row_h_line=False):
        """
        add row to the pyLatexTable withd add_row method
        :content list es: ["value1","value2"...]
        :content_flavoradd particular latex commanf
        :chunks to subdivide the row for long text
        :row_h_line put a line add_hline command after the add_row
        """
        splitted_context={}
        max_chunks = 0
        for column_index, column_content in enumerate(content):
            chunks_row=list(mit.chunked(column_content.splitlines(), chunks))
            splitted_context[column_index]=chunks_row
            if max_chunks < len(chunks_row):
                max_chunks = len(chunks_row)
        rows=[]
        latest_index=0
        for row_index in range(1,max_chunks+1):
            row=[]
            for column_index in range(0, len(content)):
                column_items = splitted_context[column_index]
                cell_content = []
                for items in column_items[latest_index:row_index]:
                    for subItem in items:
                        cell_content.append(subItem)
                cell_content = "\n".join(cell_content)
                if content_flavor:
                    cell_content=f"{cell_content}{content_flavor[column_index]}"
                row.append(NoEscape(cell_content))
            latest_index=row_index
            if pyLtexTable:
                if row_h_line:
                    pyLtexTable.add_hline()
                pyLtexTable.add_row(row)
        
        
    def get_partner_address_minipage(self, partner_id, fields=[]):
        """
        Get a minpage for formatting the partner id
        :partner_id odoo res.partner to render
        :fields fields for the partner that you would like to show in no field is passed all are rendered
        remarks:
            the field are rendered in teh followin order
            partner_id.name
            partner_id.street
            partner_id.zip partner_id.city
            partner_id.state_id.display_name
            partner_id.country_id.display_name
        """
        minipage = pylatex.MiniPage()
        if 'name' in fields or not fields:
            minipage.append(f"{partner_id.name}")
            minipage.append(pylatex.LineBreak())
        if 'street' in fields or not fields:
            minipage.append(f"{partner_id.street}")
            minipage.append(pylatex.LineBreak())
        if 'zip' in fields or not fields:
            minipage.append(f"{partner_id.zip} {partner_id.city}")
            minipage.append(pylatex.LineBreak())
        if 'state' in fields or not fields:
            minipage.append(f"{partner_id.state_id.display_name}")
            minipage.append(pylatex.LineBreak())
        if 'country' in fields or not fields:
            minipage.append(f"{partner_id.country_id.display_name}")
        return minipage
        
        