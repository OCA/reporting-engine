1. Go to Settings > Technical > Reporting > PDF Form Reports and create a new record.
2. Link with dedicated Report and empty QWeb template
3. Define how to fille the PDF fields using Odoo fields.

## Demo Data
If you installed the module with demo data, you will have a sample configuration already set up:
- A demo PDF form template for partner records
- Field mappings for name, email, and phone (simple dotted paths)
- Field mappings with deeper dotted paths like company_id.name, user_id.login, and country_id.name
- A variable for the current date

To use the demo data, simply go to the Contacts module, select a partner, and print the "Demo Partner Report".
