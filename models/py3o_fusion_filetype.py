from openerp.osv import fields, osv


class py3o_fusion_filetype(osv.Model):
    _name = 'py3o.fusion.filetype'

    _rec_name = 'human_ext'

    _columns = {
        'fusion_ext': fields.char(
            u"Fusion Extension",
            size=8,
        ),
        'human_ext': fields.char(
            u"Human readble extension",
            size=8,
        ),
    }
