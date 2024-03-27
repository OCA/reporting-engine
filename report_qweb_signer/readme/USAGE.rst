User just prints PDF documents (only Qweb PDF reports supported) as usual,
but signed PDF is automatically downloaded if this document model is configured
as indicated above.

If 'Save as attachment' is configured, signed PDF is saved as attachment and
next time saved one is downloaded without signing again. This is appropiate
when signing date is important, for example, when signing customer invoices.

You can try the signing with the demo report that is included for customers
called "Test PDF certificate".

You can set extra parameters of JSignPdf library in the system parameter
named 'report_qweb_signer.java_position_parameters', for example '-V' to
visible signature into pdf. You can also set extra parameters for Java in the
system parameter named 'report_qweb_signer.java_parameters'.
