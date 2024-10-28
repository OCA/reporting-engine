import connectorx as cx

from odoo import _, exceptions, fields, models

HELP = """
String connexion samples:

postgres://user:PASSWORD@server:port/database
mssql://user:PASSWORD@server:port/db.encrypt=true&trusted_connection=false
sqlite:///home/user/path/test.db
mysql://user:PASSWORD@server:port/database
oracle://user:PASSWORD@server:port/database
"""


class DbConfig(models.Model):
    _name = "db.config"
    _description = "External db.configuration"
    _rec_name = "name"
    _order = "name"
    _rec_names_search = ["name"]

    name = fields.Char(required=True)
    string_connexion = fields.Char(required=True, help=HELP)
    password = fields.Char(help="Not required for Sqlite")

    def _get_connexion(self):
        return self.string_connexion.replace("PASSWORD", self.password or "")

    def test_connexion(self):
        res = self._read_sql(self._get_connexion(), "SELECT 1")
        if len(res):
            # Not invalid in reality
            raise exceptions.ValidationError(_("Connexion OK !"))

    def _read_sql(self, connexion, query):
        try:
            return cx.read_sql(connexion, query, return_type="polars")
        except RuntimeError as err:
            raise exceptions.ValidationError(err) from err
        except TimeoutError as err:
            raise exceptions.ValidationError(err) from err
        except Exception as err:
            raise exceptions.ValidationError(err) from err
