# Copyright (C) 2019 - TODAY, Open Source Integrators
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


def pre_init_product_code(cr):
    cr.execute("""UPDATE product_product
        SET default_code = 'DEFAULT' || nextval('ir_default_id_seq')
        WHERE id in (SELECT distinct(pp.id)
                     FROM product_product pp
                     INNER JOIN (SELECT default_code, COUNT(*)
                                 FROM product_product
                                 GROUP BY default_code
                                 HAVING COUNT(*)>1
                                 )pp1 on pp.default_code=pp1.default_code
                                  or pp.default_code is NULL
                                  or LENGTH(pp.default_code) = 0)""")
    return True
