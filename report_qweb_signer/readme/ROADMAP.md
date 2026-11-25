- When signing multiple documents (if *Allow only one document* is disabled) then *Save
  as attachment* is not applied and signed result is not saved as attachment.
- Add more tests.
- This module is incompatible with the `account_edi_ubl_cii` module, because the PDF content is altered after rendering. See: https://github.com/odoo/odoo/blob/5977da2c93d522ece984d2fa8a31624f4b612eca/addons/account_edi_ubl_cii/models/account_move_send.py#L131C9-L140
