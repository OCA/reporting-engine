Go to *Settings \> Technical \> Reporting \> Qweb Field Options*, and
create records according to your needs.

For each record:

- Set **Model** and **Field** (required)
- Set **UoM** and **UoM Field**, or **Currency** and **Currency Field**
  only for fields of float type (optional)
- Set **Company** (optional)
- Set **Options** as a string representation of a dictionary. E.g.,
  `{"widget": "date"}`, `{"widget": "monetary"}`, or
  `{'widget': 'contact', 'fields': ['name', 'phone']}`
- Set **Digits** (only for float-type fields). The value is ignored if
  Options is set
