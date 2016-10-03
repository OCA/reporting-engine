from openerp.osv import fields, osv


class py3o_server(osv.Model):
    _name = 'py3o.server'

    _columns = {
        'url': fields.char(
            u"URL",
            size=256,
        ),
        'is_active': fields.boolean(
            u"Active",
        )
    }

    _defaults = {
        'is_active': True,
    }
