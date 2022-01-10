#. Go to *Settings* and activate the developer mode.
#. Go to *Settings > Technical > Reporting > Comment Templates*.
#. Create a new record.
#. Define the Company the template is linked or leave default for all companies.
#. Define the Partner the template is linked or leave default for all partners.
#. Define the Model, Domain the template is linked.
#. Define the Position where the template will be printed:

   * above document lines
   * below document lines

You should have at least one template with Default field set, if you choose a Partner the template is deselected as a Default one.
If you create a new template with the same configuration (Model, Domain, Position) and set it as Default, the previous one will be deselected as a default one.

The template is a html field which will be rendered just like a mail template, so you can use variables like ${object}, ${user}, ${ctx} to add dynamic content.

Change the report related to the model from configuration and add a statement like:

<t t-foreach="o.comment_template_ids.filtered(lambda x: x.position == 'before_lines')" t-as="comment_template_top">
  <div t-raw="o.render_comment(comment_template_top)" />

</t>


<t t-foreach="o.comment_template_ids.filtered(lambda x: x.position == 'after_lines')" t-as="comment_template_bottom">
    <div t-raw="o.render_comment(comment_template_bottom)" />

</t>

You should always use t-if since the method returns False if no template is found.

If you want to use Qweb templates, or different context, you can specify it just like in
mail.render.mixin with parameters:

- engine: "jinja" or "qweb",
- add_context: dict with your own context,
- post_process: perform a post processing on rendered result

so you could use it :

<t t-foreach="o.comment_template_ids.filtered(lambda x: x.position == 'before_lines')" t-as="comment_template_top">
    <div t-raw="o.render_comment(comment_template_top, engine='qweb', add_context={my dict}, postprocess=True)" />

</t>
