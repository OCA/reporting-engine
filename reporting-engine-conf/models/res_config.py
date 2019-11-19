# -*- coding: utf-8 -*-
import openerp
from openerp import api, fields, models, _

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    
    module_bi_sql_editor = fields.Boolean(string='BI-SQL Editor',
        help= 'This module extends the functionality of reporting, to support creation \n'
              'of extra custom reports. \n'
              'It allows user to write a custom SQL request. (Generally, admin users) \n'

              'Once written, a new model is generated, and user can map the selected field \n'
              'with odoo fields. \n'
              'Then user ends the process, creating new menu, action and graph view. \n'

              'Technically, the module create SQL View (or materialized view, if option is \n'
              'checked). Materialized view duplicates datas, but request are fastest. If \n'
              'materialized view is enabled, this module will create a cron task to refresh \n'
              'the data). \n'
             '-This installs the module bi_sql_editor.')
    
    module_kpi = fields.Boolean(string='KPI',
         help= ' This module provides the basis for creating key performance indicators, \n'
                ' including static and dynamic thresholds (SQL query or Python code), \n'
                ' on local and remote data sources. \n'

                ' The module also provides the mecanism to update KPIs automatically. \n'
                ' A scheduler is executed every hour and updates the KPI values, based \n'
                ' on the periodicity of each KPI. KPI computation can also be done \n'
                ' manually. \n'

                ' A threshold is a list of ranges and a range is: \n'

                ' * a name (like Good, Warning, Bad) \n'
                ' * a minimum value (fixed, sql query or python code) \n'
                ' * a maximum value (fixed, sql query or python code) \n'
                ' * color (RGB code like #00FF00 for green, #FFA500 for orange, #FF0000 for red) \n'
             '-This installs the module kpi.')

    module_report_context = fields.Boolean(string='Report Context',
         help='This module adds a context variable to reports. A possible use for this \n'
            'context could be hiding some fields or many other configuration options. \n'
             '-This installs the module report_context.')

    module_report_py3o = fields.Boolean(string='Report py3o',
         help='The py3o reporting engine is a reporting engine for Odoo based on'
                'Libreoffice <http://www.libreoffice.org/>_: \n'

                '* the report is created with Libreoffice (ODT or ODS), \n'
                '* the report is stored on the server in OpenDocument format (.odt or .ods file) \n'
                '* the report is sent to the user in OpenDocument format or in any  \n'
                'output format supported by Libreoffice (PDF, HTML, DOC, DOCX, Docbook, XLS, etc.) \n'

                'The key advantages of a Libreoffice based reporting engine are: \n'

                ' * no need to be a developer to create or modify a report:  \n'
                ' the report is created and modified with Libreoffice. So this reporting engine \n'
                '  has a full WYSIWYG report development tool! \n'
                ' * For a PDF report in A4/Letter format, its easier to develop it with  \n'
                ' a tool such as Libreoffice that is designed to create A4/Letter documents \n' 
                ' than to develop it in HTML/CSS, also some print peculiarities (backgrounds, margin boxes) \n'
                '  are not very well supported by the HTML/CSS based solutions. \n'
                ' * If you want your users to be able to modify the document after its generation by Odoo, \n'
                '  just configure the document with ODT output (or DOC or DOCX) and the user will be able \n'
                '   to modify the document with Libreoffice (or Word) after its generation by Odoo. \n'
                ' * Easy development of spreadsheet reports in ODS format (XLS output possible). \n'

                'This module *report_py3o* is the base module for the Py3o reporting engine. \n'
                 'If used alone, it will spawn a libreoffice process for each ODT to PDF (or ODT to DOCX, ..) \n'
                  'document conversion. This is slow and can become a problem if you have a lot of reports  \n'
                  'to convert from ODT to another format. In this case, you should consider the additionnal module \n' 'report_py3o_fusion_server* which is designed to work with a libreoffice daemon. \n'
                   'With *report_py3o_fusion_server*, the technical environnement is more complex \n'
                    'to setup because you have to install additionnal software  \n'
                    'components and run 2 daemons, but you have much better performances and you can configure \n'
                'the libreoffice PDF export options in Odoo (allows to generate PDF forms, PDF/A documents, \n' 'password-protected PDFs, watermarked PDFs, etc.). \n'
             '-This installs the module report_py3o.')

    module_report_py3o_fusion_server = fields.Boolean(string='Report py3o Fusion Server',
         help='This module was written to let a py3o fusion server handle format conversion instead of local libreoffice. \n' 
                'If you install this module above the *report_py3o* module, you will '
                'have to deploy additionnal software  components and run 3 daemons (libreoffice,\n'
                ' py3o.fusion and py3o.renderserver).  \n'
                'This additionnal complexiy comes with several advantages: \n'

                '* much better performances (Libreoffice runs permanently in the background, '
                'no need to spawn a new Libreoffice  instance upon every document conversion). \n'
             '-This installs the module report_py3o_fusion_server.')

    module_report_qr = fields.Boolean(string='Report QR',
         help='This module allows to print QR in better structure than the standard odoo. \n'
             '-This installs the module report_qr.')

    module_report_qweb_parameter = fields.Boolean(string='Report QWEB Parameter',
         help= ' This module allows you to add new parameters on QWeb reports. \n'
              ' Currently, we have defined a field maximum on a report and a validation of \n'
              ' maximal and minimal size. \n'
              ' It is useful on xml reports in order to validate length. \n'
              ' XML are sometimes XSD dependant and we must validate its format. \n'
              ' For example, in spanish facturae (http://www.facturae.gob.es/Paginas/Index.aspx), where \n'
              ' length and format must be validated in several fields in order to send an invoice. \n'
             '-This installs the module report_qweb_parameter.')

    module_report_qweb_signer = fields.Boolean(string='Report QWEB Signer',
         help='This module extends the functionality of report module to sign \n'
              'PDFs using a PKCS#12 certificate. \n'
             '-This installs the module report_qweb_signer.')

    module_report_substitute = fields.Boolean(string='Report Substitute',
         help='This module allows you to create substitution rules for report actions. \n'
              'A typical use case is to replace a standard report by alternative reports \n'
              'when some conditions are met. For instance, it allows to configure alternate \n'
              'reports for different companies. \n'
             '-This installs the module report_substitute.')

    module_report_wkhtmltopdf_param = fields.Boolean(string='Report Wkhtmltopdf Parameter',
         help='This module allows you to add new parameters for a paper format which are \n'
              'then forwarded to wkhtmltopdf command as arguments. To display the arguments \n'
              'that wkhtmltopdf accepts go to your command line and type wkhtmltopdf -H . \n'

              'A commonly used parameter in Odoo is *--disable-smart-shrinking*, that will \n'
              'disable the automatic resizing of the PDF when converting. This is \n'
              'important when you intend to have a layout that conforms to certain alignment. \n'
              'It is very common whenever you need to conform the PDF to a predefined \n'
              'layoyut (e.g. checks, official forms,...). \n'
             '-This installs the module report_wkhtmltopdf_param.')

    module_report_xlsx = fields.Boolean(string='Report xlsx',
         help='This module provides a basic report class to generate xlsx report. \n'
             '-This installs the module report_xlsx.')

    module_report_xlsx_helper = fields.Boolean(string='Report xlsx Helper',
         help='This module provides a set of tools to facilitate the creation of excel reports with format xlsx.\n'
             '-This installs the module report_xlsx_helper.')

    module_report_xlsx_helper_demo = fields.Boolean(string='Report xlsx Helper Demo',
         help= 'This module demonstrates the capabilities or the report_xlsx_helper module via'
                'a basic example. \n'
             '-This installs the module report_xlsx_helper_demo.')

    module_report_xml = fields.Boolean(string='Report XML',
         help='This module was written to extend the functionality of the reporting engine to \n'
              'support XML reports and allow modules to generate them by code or by QWeb \n'
              'templates. \n'
             '-This installs the module report_xml.')


    