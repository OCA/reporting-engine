###################################################################################
#
#    Copyright (c) 2017-2019 MuK IT GmbH.
#
#    This file is part of MuK Converter 
#    (see https://mukit.at).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program. If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################

import os
import io
import base64
import shutil
import urllib
import logging
import tempfile
import mimetypes

from subprocess import Popen
from subprocess import PIPE
from subprocess import CalledProcessError

from contextlib import closing

from odoo.tools import config
from odoo.tools.mimetypes import guess_mimetype

from odoo.addons.muk_utils.tools.file import guess_extension

_logger = logging.getLogger(__name__)

UNOCONV_FORMATS = [
    "bib", "bmp", "csv", "dbf", "dif", "doc", "doc6", "doc95", "docbook", "docx", "docx7", "emf",
    "eps", "fodg", "fodp", "fods", "fodt", "gif", "html", "jpg", "latex", "mediawiki", "met", "odd",
    "odg", "odp", "ods", "odt", "ooxml", "otg", "otp", "ots", "ott", "pbm", "pct", "pdb", "pdf", "pgm",
    "png", "pot", "potm", "ppm", "pps", "ppt", "pptx", "psw", "pwp", "pxl", "ras", "rtf", "sda", "sdc",
    "sdc3", "sdc4", "sdd", "sdd3", "sdd4", "sdw", "sdw3", "sdw4", "slk", "stc", "std", "sti", "stw",
    "svg", "svm", "swf", "sxc", "sxd", "sxd3", "sxd5", "sxi", "sxw", "text", "tiff", "txt", "uop", "uos",
    "uot", "vor", "vor3", "vor4", "vor5", "wmf", "wps", "xhtml", "xls", "xls5", "xls95", "xlsx", "xlt",
    "xlt5", "xlt95", "xpm""bib", "bmp", "csv", "dbf", "dif", "doc", "doc6", "doc95", "docbook", "docx",
    "docx7", "emf", "eps", "fodg", "fodp", "fods", "fodt", "gif", "html", "jpg", "latex", "mediawiki",
    "met", "odd", "odg", "odp", "ods", "odt", "ooxml", "otg", "otp", "ots", "ott", "pbm", "pct", "pdb",
    "pdf", "pgm", "png", "pot", "potm", "ppm", "pps", "ppt", "pptx", "psw", "pwp", "pxl", "ras", "rtf",
    "sda", "sdc", "sdc3", "sdc4", "sdd", "sdd3", "sdd4", "sdw", "sdw3", "sdw4", "slk", "stc", "std",
    "sti", "stw", "svg", "svm", "swf", "sxc", "sxd", "sxd3", "sxd5", "sxi", "sxw", "text", "tiff",
    "txt", "uop", "uos", "uot", "vor", "vor3", "vor4", "vor5", "wmf", "wps", "xhtml", "xls", "xls5",
    "xls95", "xlsx", "xlt", "xlt5", "xlt95", "xpm"
]

UNOCONV_IMPORTS = [
    "bmp", "csv", "dbf", "dif", "doc", "docx", "dot", "emf", "eps", "epub", "fodg", "fodp", "fods",
    "fodt", "gif", "gnm", "gnumeric", "htm", "html", "jpeg", "jpg", "met", "mml", "odb", "odf", "odg",
    "odp", "ods", "odt", "pbm", "pct", "pdb", "pdf", "pgm", "png", "pot", "ppm", "pps", "ppt", "pptx",
    "psw", "pxl", "ras", "rtf", "sda", "sdc", "sdd", "sdp", "sdw", "sgl", "slk", "stc", "std", "sti",
    "stw", "svg", "svm", "swf", "sxc", "sxd", "sxi", "sxm", "sxw", "tif", "tiff", "txt", "uof", "uop",
    "uos", "uot", "vor", "wmf", "wri", "xls", "xlsx", "xlt", "xlw", "xml", "xpm""bmp", "csv", "dbf",
    "dif", "doc", "docx", "dot", "emf", "eps", "epub", "fodg", "fodp", "fods", "fodt", "gif", "gnm",
    "gnumeric", "htm", "html", "jpeg", "jpg", "met", "mml", "odb", "odf", "odg", "odp", "ods", "odt",
    "pbm", "pct", "pdb", "pdf", "pgm", "png", "pot", "ppm", "pps", "ppt", "pptx", "psw", "pxl", "ras",
    "rtf", "sda", "sdc", "sdd", "sdp", "sdw", "sgl", "slk", "stc", "std", "sti", "stw", "svg", "svm",
    "swf", "sxc", "sxd", "sxi", "sxm", "sxw", "tif", "tiff", "text", "uof", "uop", "uos", "uot", "vor",
    "wmf", "wri", "xls", "xlsx", "xlt", "xlw", "xml", "xpm"
]

class UnoconvConverter(object):
    
    @property
    def formats(self):
        return UNOCONV_FORMATS
    
    @property
    def imports(self):
        return UNOCONV_IMPORTS
    
    def environ(self):
        env = os.environ.copy()
        uno_path = config.get('uno_path', False)
        if uno_path:
            env['UNO_PATH'] = config['uno_path']   
        return env

    def convert(self, binary, mimetype=None, filename=None, export="binary", doctype="document", format="pdf"):
        """ Converts a binary value to the given format.
        
            :param binary: The binary value.
            :param mimetype: The mimetype of the binary value.
            :param filename: The filename of the binary value.
            :param export: The output format (binary, file, base64).
            :param doctype: Specify the document type (document, graphics, presentation, spreadsheet).
            :param format: Specify the output format for the document.
            :return: Returns the output depending on the given format.
            :raises ValueError: The file extension could not be determined or the format is invalid.
        """
        extension = guess_extension(filename=filename, mimetype=mimetype, binary=binary)
        if not extension:
            raise ValueError("The file extension could not be determined.")
        if format not in self.formats:
            raise ValueError("Invalid export format.")
        if extension not in self.imports:
            raise ValueError("Invalid import format.")
        tmp_dir = tempfile.mkdtemp()
        try:
            tmp_wpath = os.path.join(tmp_dir, "tmpfile." + extension)
            tmp_ppath = os.path.join(tmp_dir, "tmpfile." + format)
            if os.name == 'nt':
                tmp_wpath = tmp_wpath.replace("\\", "/")
                tmp_ppath = tmp_ppath.replace("\\", "/")
            with closing(open(tmp_wpath, 'wb')) as file:
                file.write(binary)    
            shell = True if os.name in ('nt', 'os2') else False
            args = ['unoconv', '--format=%s' % format, '--output=%s' % tmp_ppath, tmp_wpath]
            process = Popen(args, stdout=PIPE, env=self.environ(), shell=shell)
            outs, errs = process.communicate()
            return_code = process.wait()
            if return_code:
                raise CalledProcessError(return_code, args, outs, errs)
            with closing(open(tmp_ppath, 'rb')) as file:
                if export == 'file':
                    output = io.BytesIO()
                    output.write(file.read())
                    output.close()
                    return output
                elif export == 'base64':
                    return base64.b64encode(file.read())
                else:
                    return file.read()
        except CalledProcessError:
            _logger.exception("Error while running unoconv.")
            raise
        except OSError:
            _logger.exception("Error while running unoconv.")
            raise
        finally:
            shutil.rmtree(tmp_dir)

unoconv = UnoconvConverter()