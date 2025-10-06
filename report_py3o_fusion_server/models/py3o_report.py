# © 2013 XCG Consulting <http://odoo.consulting>
# © 2016 ACSONE SA/NV
# © 2017 Therp BV <http://therp.nl>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import logging
import tempfile
from datetime import datetime

from odoo import models

logger = logging.getLogger(__name__)

try:
    from py3o.formats import Formats
except ImportError:
    logger.debug("Cannot import py3o.formats")
try:
    import uno
except ImportError:
    logger.debug("Cannot import uno")
    uno = False
try:
    from com.sun.star.beans import PropertyValue
except ImportError:
    logger.debug("Cannot import com.sun.star.beans")


class Py3oReport(models.TransientModel):
    _inherit = "py3o.report"

    def _create_single_report(self, model_instance, data):
        """This function to generate our py3o report"""
        self.ensure_one()
        report = self.ir_actions_report_id
        py3o_server = report.py3o_server_id
        if not py3o_server or not uno:
            return super()._create_single_report(model_instance, data)
        filetype = report.py3o_filetype
        uno_filter_data = []
        if filetype == "pdf":
            options = report.pdf_options_id or py3o_server.pdf_options_id
            if options:
                pdf_options_dict = options.odoo2libreoffice_options()
                logger.debug("PDF export options: %s", pdf_options_dict)
                for pdf_opt_key, pdf_opt_val in pdf_options_dict.items():
                    if isinstance(pdf_opt_val, bool | int | str) and isinstance(
                        pdf_opt_key, str
                    ):
                        uno_filter_data.append(
                            PropertyValue(Name=pdf_opt_key, Value=pdf_opt_val)
                        )

        logger.info(
            "Connecting to LibreOffice on %s to convert report %s to %s",
            py3o_server.display_name,
            report.report_name,
            filetype,
        )
        start_chrono = datetime.now()
        uno_local_ctx = uno.getComponentContext()
        uno_resolver = uno_local_ctx.ServiceManager.createInstanceWithContext(
            "com.sun.star.bridge.UnoUrlResolver", uno_local_ctx
        )
        uno_url = (
            f"uno:socket,host={py3o_server.host.strip()},"
            f"port={py3o_server.port};urp;StarOffice.ComponentContext"
        )
        logger.debug("uno_url=%s", uno_url)
        try:
            uno_ctx = uno_resolver.resolve(uno_url)
            logger.info(
                "Connection to LibreOffice established on %s", py3o_server.display_name
            )
        except Exception as e:
            logger.warning(
                "Failed to connect to LibreOffice on %s. Error: %s",
                py3o_server.display_name,
                e,
            )
            return super()._create_single_report(model_instance, data)

        uno_desktop = uno_ctx.getByName("/singletons/com.sun.star.frame.theDesktop")
        result_path = super(
            Py3oReport, self.with_context(report_py3o_skip_conversion=True)
        )._create_single_report(model_instance, data)
        logger.debug("Input result_path=%s", result_path)

        uno_import_url = uno.systemPathToFileUrl(result_path)
        uno_input_properties = [PropertyValue(Name="ReadOnly", Value=True)]

        try:
            # API doc: https://api.libreoffice.org/docs/idl/ref/
            # interfacecom_1_1sun_1_1star_1_1frame_1_1XComponentLoader.html
            uno_document = uno_desktop.loadComponentFromURL(
                uno_import_url, "_default", 0, uno_input_properties
            )
            logger.info("LibreOffice successfully loaded the document")
        except Exception as e:
            logger.warning(
                "LibreOffice failed to load the document from %s. Error: %s",
                uno_import_url,
                e,
            )
            return super()._create_single_report(model_instance, data)
        if not uno_document:
            logger.warning(
                "LibreOffice failed to load the document from %s. No specific error.",
                uno_import_url,
            )
            return super()._create_single_report(model_instance, data)
        # It doesn't work when the same path is used as input and output,
        # so we create a file dedicated to the output
        _out_fd, out_result_path = tempfile.mkstemp(
            prefix="py3o.report.tmp.", suffix=f".{filetype}"
        )
        logger.debug("out_result_path=%s", out_result_path)
        uno_out_url = uno.systemPathToFileUrl(out_result_path)
        # py3o.formats doesn't take into account the source format to decide
        # the right filter. For pdf, il will always give "writer_pdf_Export"
        # although we should use "calc_pdf_Export" if source document is ODS
        # TODO stop using py3o.formats and re-write this mess
        uno_filtername = Formats()._formats[filetype].odfname
        logger.debug("uno_filtername=%s uno_out_url=%s", uno_filtername, uno_out_url)
        uno_output_properties = [
            PropertyValue(Name="FilterName", Value=uno_filtername),
            PropertyValue(Name="Overwrite", Value=True),
            PropertyValue(
                Name="FilterData",
                Value=uno.Any("[]com.sun.star.beans.PropertyValue", uno_filter_data),
            ),
        ]
        try:
            uno_document.storeToURL(uno_out_url, uno_output_properties)
        except Exception as err:
            logger.warning(
                "Conversion of report %s to %s with LibreOffice failed. Error: %s",
                report.report_name,
                filetype,
                err,
            )
            logger.warning(
                "Make sure the source format can really be converted to %s.", filetype
            )
            return super()._create_single_report(model_instance, data)
        finally:
            # Should we call uno_desktop.terminate() ??
            uno_document.close(True)
            logger.debug("document has been closed.")

        # TODO: test that the output has the right format
        # by analysing the beginning of the file
        # To trigger the bug: change "FilterName" by "toto" in uno_output_properties
        end_chrono = datetime.now()
        convert_seconds = (end_chrono - start_chrono).total_seconds()
        logger.info(
            "Report %s converted to %s in %s seconds",
            report.report_name,
            filetype,
            convert_seconds,
        )
        if len(model_instance) == 1:
            self._postprocess_report(model_instance, out_result_path)
        return out_result_path
