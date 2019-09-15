(after installing `sale_management` application)

#. Go to ``Sales > Catalog > Product Variants``.
#. Click on "Create" button for creating a new one.
#. On the field "Product Template", select a product template that has several
   attributes.
#. A table with the attributes of the template will appear below.
#. Select all the attribute values and click on "Save" button.
#. A new product variant will be created for that attributes.
#. An error will raise if there's another variant with the same attribute
   values or if you haven't filled all the required values.

**Developers**

To use product configurator in your model, you need to:

#. The product.configurator is an abstract model, hence, to be used it must be
   inherited in your model:
#. If the model you're inheriting has ``name`` attribute, and it uses the
   related parameter you must override it.

::

    class AModel(models.Model):
        _inherit = ['module.model', 'product.configurator']
        name = fields.Char(related="delegated_field.related_field")
