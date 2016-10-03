from openerp.osv import fields, osv


class py3o_template(osv.Model):
    _name = 'py3o.template'

    _columns = {
        'name': fields.char(
            u"Name",
        ),

        'py3o_template_data': fields.binary(
            u"LibreOffice template",
        ),

        'filetype': fields.selection(
            [
                ('odt', u"ODF Text Document"),
                ('ods', u"ODF Spreadsheet"),
            ],
            u"LibreOffice Template File Type",
            required=True,
        ),
    }

    _defaults = {
        'filetype': 'odt'
    }
