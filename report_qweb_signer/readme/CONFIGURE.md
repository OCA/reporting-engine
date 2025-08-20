To start signing PDF reports you'll need first to configure your desired certificate. To do so:

- Go to *Settings > General Settings* and then to the section *Certificates and Keys*. Then click on **Certificates**.
- Add the cert you want to use: upload the file and set the password.

Now you need to configure the reports using this certificate:

- Go to *Settings > Thecnical > Reporting > Reports*.
- Search for the pdf report you want to sign.
- In the report form, open the **Sign** tab.
- Choose the **Certificate** you created before.
- Optionally, you can set:
  - **Allow to sign only one document**: disallow signing a pdf that contains multiple docs.
  - **Save as attachment**: Set the signed document report file name pattern. Example: `(object.name or '').replace('/','_') + '.signed.pdf'`
  - **Signing domain**: Filter the document that will be signed. Example: `[('move_type','=','out_invoice'), ('state', '=', 'posted')]`
