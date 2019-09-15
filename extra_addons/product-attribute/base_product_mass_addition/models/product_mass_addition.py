# © 2019 Today Akretion
# @author Pierrick Brun <pierrick.brun@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo import models, api
from odoo.tests.common import Form


class ProductMassAddition(models.AbstractModel):
    _name = 'product.mass.addition'
    _description = 'inherit this to add a mass product addition function\
                    to your model'

    @api.model
    def _common_action_keys(self):
        """ Call it in your own child module
        """
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'target': 'current',
            'context': {'parent_id': self.id, 'parent_model': self._name},
            'view_mode': 'tree',
        }

    def _prepare_quick_line(self, product):
        res = self._get_quick_line_qty_vals(product)
        res.update({'product_id': product.id})
        return res

    def _get_quick_line(self, product):
        raise NotImplementedError

    def _add_quick_line(self, product, lines_key=''):
        if not lines_key:
            raise NotImplementedError
        vals = self._prepare_quick_line(product)
        vals = self._complete_quick_line_vals(vals)
        self.write({lines_key: [(0, 0, vals)]})

    def _update_quick_line(self, product, line):
        if product.qty_to_process:
            # apply the on change to update price unit if depends on qty
            vals = self._get_quick_line_qty_vals(product)
            vals['id'] = line.id
            vals = self._complete_quick_line_vals(vals)
            line.write(vals)
        else:
            line.unlink()

    def _get_quick_line_qty_vals(self, product):
        raise NotImplementedError

    def _complete_quick_line_vals(self, vals, lines_key=''):
        if not lines_key:
            raise NotImplementedError
        form_parent = Form(self)
        form_line = False
        if vals.get('id'):
            for index, line in enumerate(self[lines_key]):
                if line.id == vals.get('id'):
                    form_line = getattr(form_parent, lines_key).edit(index)
                    del vals['id']
                    break
        init_keys = ['product_id']
        init_vals = [(key, val) for key, val in vals.items()
                     if key in init_keys]
        if not form_line:
            form_line = getattr(form_parent, lines_key).new()
            form_line._values.update(init_vals)
            form_line._perform_onchange(init_keys)

        update_keys = [key for key in vals.keys() if key not in init_keys]
        update_vals = [(key, val) for key, val in vals.items()
                       if key not in init_keys]
        form_line._values.update(update_vals)
        form_line._perform_onchange(update_keys)
        return form_line._values
