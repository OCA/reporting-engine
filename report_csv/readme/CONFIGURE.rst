In case the exported CSV report should be encoded in another system than UTF-8, following
fields of the report record (*Settings > Technical > Reports*) should be populated accordingly.

* Encoding: set an encoding system (such as cp932)
* Encode Error Handling: select 'Ignore' or 'Replace' as necessary.

  * 'Ignore': in case of an encoding error, the problematic character will be removed from the exported file.
  * 'Replace': in case of an encoding error, the problematic character will be replaced with '?' symbol.
  * Leaving the field blank: in case of an encoding error, the report generation fails with an error message.
