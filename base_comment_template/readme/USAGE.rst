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

<p t-if="o.get_comment_template('before_lines', o.company_id.id, o.partner_id and o.partner_id.id or False)">

    <span t-raw="o.get_comment_template('before_lines', o.company_id.id, o.partner_id and o.partner_id.id or False)"/>

</p>

<p t-if="o.get_comment_template('after_lines', o.company_id.id, o.partner_id and o.partner_id.id or False)">

    <span t-raw="o.get_comment_template('after_lines', o.company_id.id, o.partner_id and o.partner_id.id or False)"/>

</p>

You should always use t-if since the method returns False if no template is found.
