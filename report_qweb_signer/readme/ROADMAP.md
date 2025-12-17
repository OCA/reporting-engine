- This version 18.0 depends on pyhanko-cli for signing the documents, which isn't ideal
  at all but avoids the dependency hell coming from cryptography requisites.
- In Odoo 19.0 Odoo implemented their own signing mechanism. We could backport it but
  it depends on python 12 which supports the proper cryptography library version and
  that would leave out any infrastructure using lower versions. So: for v19 we should
  get rid of all that external stuff and just use the core one. (ref: https://github.com/odoo/odoo/pull/194698)
- When signing multiple documents (if *Allow only one document* is disabled) then *Save
  as attachment* is not applied and signed result is not saved as attachment.
- Add more tests.
- This module is incompatible with the `account_edi_ubl_cii` module, because the PDF content is altered after rendering. See: https://github.com/odoo/odoo/blob/5977da2c93d522ece984d2fa8a31624f4b612eca/addons/account_edi_ubl_cii/models/account_move_send.py#L131C9-L140
