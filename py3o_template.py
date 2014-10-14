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
    }
