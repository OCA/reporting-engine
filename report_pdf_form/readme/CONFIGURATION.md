1. Go to Settings > Technical > Reporting > PDF Form Reports and create a new record.
2. Link with a dedicated Report and empty QWeb template.
3. Upload your PDF form file as an attachment (this is required).
4. Define how to fill the PDF fields using Odoo fields.

## Uploading PDF Forms
Yes, users must upload a PDF file that contains form fields. The PDF should have interactive form fields that can be filled with data from Odoo records. You can create these PDF forms using tools like:
- LibreOffice Draw
- Scribus
- Adobe Acrobat
- Online tools like docfly.com

## Demo Data
If you installed the module with demo data, you will have a sample configuration already set up:
- A demo PDF form template for partner records
- Field mappings for name, email, and phone (simple dotted paths)
- Field mappings with deeper dotted paths like company_id.name, user_id.login, and country_id.name
- A variable for the current date

To use the demo data, simply go to the Contacts module, select a partner, and print the "Demo Partner Report".