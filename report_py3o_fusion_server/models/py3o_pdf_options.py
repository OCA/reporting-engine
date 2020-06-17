# Copyright 2018 Akretion (http://www.akretion.com)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)


class Py3oPdfOptions(models.Model):
    _name = "py3o.pdf.options"
    _description = "Define PDF export options for Libreoffice"

    name = fields.Char(required=True)
    # GENERAL TAB
    # UseLosslessCompression (bool)
    image_compression = fields.Selection(
        [("lossless", "Lossless Compression"), ("jpeg", "JPEG Compression")],
        string="Image Compression",
        default="jpeg",
    )
    # Quality (int)
    image_jpeg_quality = fields.Integer(
        string="Image JPEG Quality",
        default=90,
        help="Enter a percentage between 0 and 100.",
    )
    # ReduceImageResolution (bool) and MaxImageResolution (int)
    image_reduce_resolution = fields.Selection(
        [
            ("none", "Disable"),
            ("75", "75 DPI"),
            ("150", "150 DPI"),
            ("300", "300 DPI"),
            ("600", "600 DPI"),
            ("1200", "1200 DPI"),
        ],
        string="Reduce Image Resolution",
        default="300",
    )
    watermark = fields.Boolean("Sign With Watermark")
    # Watermark (string)
    watermark_text = fields.Char("WaterMark Text")
    # UseTaggedPDF (bool)
    tagged_pdf = fields.Boolean("Tagged PDF (add document structure)")
    # SelectPdfVersion (int)
    # 0 = PDF 1.4 (default selection).
    # 1 = PDF/A-1 (ISO 19005-1:2005)
    pdfa = fields.Boolean(
        "Archive PDF/A-1a (ISO 19005-1)",
        help="If you enable this option, you will not be able to "
        "password-protect the document or apply other security settings.",
    )
    #  ExportFormFields (bool)
    pdf_form = fields.Boolean("Create PDF Form", default=True)
    # FormsType (int)
    pdf_form_format = fields.Selection(
        [("0", "FDF"), ("1", "PDF"), ("2", "HTML"), ("3", "XML")],
        string="Submit Format",
        default="0",
    )
    # AllowDuplicateFieldNames (bool)
    pdf_form_allow_duplicate = fields.Boolean("Allow Duplicate Field Names")
    # ExportBookmarks (bool)
    export_bookmarks = fields.Boolean("Export Bookmarks", default=True)
    # ExportPlaceholders (bool)
    export_placeholders = fields.Boolean("Export Placeholders", default=True)
    # ExportNotes (bool)
    export_comments = fields.Boolean("Export Comments")
    # ExportHiddenSlides (bool) ??
    export_hidden_slides = fields.Boolean("Export Automatically Insered Blank Pages")
    # Doesn't make sense to have the option "View PDF after export" ! :)
    # INITIAL VIEW TAB
    # InitialView (int)
    initial_view = fields.Selection(
        [("0", "Page Only"), ("1", "Bookmarks and Page"), ("2", "Thumbnails and Page")],
        string="Panes",
        default="0",
    )
    # InitialPage (int)
    initial_page = fields.Integer(string="Initial Page", default=1)
    # Magnification (int)
    magnification = fields.Selection(
        [
            ("0", "Default"),
            ("1", "Fit in Window"),
            ("2", "Fit Width"),
            ("3", "Fit Visible"),
            ("4", "Zoom"),
        ],
        string="Magnification",
        default="0",
    )
    # Zoom (int)
    zoom = fields.Integer(
        string="Zoom Factor", default=100, help="Possible values: from 50 to 1600"
    )
    # PageLayout (int)
    page_layout = fields.Selection(
        [
            ("0", "Default"),
            ("1", "Single Page"),
            ("2", "Continuous"),
            ("3", "Continuous Facing"),
        ],
        string="Page Layout",
        default="0",
    )
    # USER INTERFACE TAB
    # ResizeWindowToInitialPage (bool)
    resize_windows_initial_page = fields.Boolean(
        string="Resize Windows to Initial Page"
    )
    # CenterWindow (bool)
    center_window = fields.Boolean(string="Center Window on Screen")
    # OpenInFullScreenMode (bool)
    open_fullscreen = fields.Boolean(string="Open in Full Screen Mode")
    # DisplayPDFDocumentTitle (bool)
    display_document_title = fields.Boolean(string="Display Document Title")
    # HideViewerMenubar (bool)
    hide_menubar = fields.Boolean(string="Hide Menubar")
    # HideViewerToolbar (bool)
    hide_toolbar = fields.Boolean(string="Hide Toolbar")
    # HideViewerWindowControls (bool)
    hide_window_controls = fields.Boolean(string="Hide Windows Controls")
    # OpenBookmarkLevels (int)  -1 = all (default)  from 1 to 10
    open_bookmark_levels = fields.Selection(
        [
            ("-1", "All Levels"),
            ("1", "1"),
            ("2", "2"),
            ("3", "3"),
            ("4", "4"),
            ("5", "5"),
            ("6", "6"),
            ("7", "7"),
            ("8", "8"),
            ("9", "9"),
            ("10", "10"),
        ],
        default="-1",
        string="Visible Bookmark Levels",
    )
    # LINKS TAB
    # ExportBookmarksToPDFDestination (bool)
    export_bookmarks_named_dest = fields.Boolean(
        string="Export Bookmarks as Named Destinations"
    )
    # ConvertOOoTargetToPDFTarget (bool)
    convert_doc_ref_to_pdf_target = fields.Boolean(
        string="Convert Document References to PDF Targets"
    )
    # ExportLinksRelativeFsys (bool)
    export_filesystem_urls = fields.Boolean(string="Export URLs Relative to Filesystem")
    # PDFViewSelection -> mnDefaultLinkAction (int)
    cross_doc_link_action = fields.Selection(
        [
            ("0", "Default"),
            ("1", "Open with PDF Reader Application"),
            ("2", "Open with Internet Browser"),
        ],
        string="Cross-document Links",
        default="0",
    )
    # SECURITY TAB
    # EncryptFile (bool)
    encrypt = fields.Boolean("Encrypt")
    # DocumentOpenPassword (char)
    document_password = fields.Char(string="Document Password")
    # RestrictPermissions (bool)
    restrict_permissions = fields.Boolean("Restrict Permissions")
    # PermissionPassword (char)
    permission_password = fields.Char(string="Permission Password")
    # TODO PreparedPasswords  + PreparedPermissionPassword
    # I don't see those fields in the LO interface !
    # But they are used in the LO code...
    # Printing (int)
    printing = fields.Selection(
        [
            ("0", "Not Permitted"),
            ("1", "Low Resolution (150 dpi)"),
            ("2", "High Resolution"),
        ],
        string="Printing",
        default="2",
    )
    # Changes (int)
    changes = fields.Selection(
        [
            ("0", "Not Permitted"),
            ("1", "Inserting, Deleting and Rotating Pages"),
            ("2", "Filling in Form Fields"),
            ("3", "Commenting, Filling in Form Fields"),
            ("4", "Any Except Extracting Pages"),
        ],
        string="Changes",
        default="4",
    )
    # EnableCopyingOfContent (bool)
    content_copying_allowed = fields.Boolean(
        string="Enable Copying of Content", default=True
    )
    # EnableTextAccessForAccessibilityTools (bool)
    text_access_accessibility_tools_allowed = fields.Boolean(
        string="Enable Text Access for Accessibility Tools", default=True
    )

    """
     DIGITAL SIGNATURE TAB
     This will be possible but not easy
     Because the certificate parameter is a pointer to a certificate
     already registered in LO
     On Linux LO reuses the Mozilla certificate store (on Windows the
     one from Windows)
     But there seems to be some possibilities to send this certificate via API
     It seems you can add temporary certificates during runtime:
     https://api.libreoffice.org/docs/idl/ref/
     interfacecom_1_1sun_1_1star_1_1security_1_1XCertificateContainer.html
     Here is an API to retrieve the known certificates:
     https://api.libreoffice.org/docs/idl/ref/
     interfacecom_1_1sun_1_1star_1_1xml_1_1crypto_1_1XSecurityEnvironment.html
     Thanks to 'samuel_m' on libreoffice-dev IRC chan for pointing me to this
    """

    @api.constrains(
        "image_jpeg_quality",
        "initial_page",
        "pdfa",
        "cross_doc_link_action",
        "magnification",
        "zoom",
    )
    def check_pdf_options(self):
        for opt in self:
            if opt.image_jpeg_quality > 100 or opt.image_jpeg_quality < 1:
                raise ValidationError(
                    _(
                        "The parameter Image JPEG Quality must be between 1 %%"
                        " and 100 %% (current value: %s %%)"
                    )
                    % opt.image_jpeg_quality
                )
            if opt.initial_page < 1:
                raise ValidationError(
                    _(
                        "The initial page parameter must be strictly positive "
                        "(current value: %d)"
                    )
                    % opt.initial_page
                )
            if opt.pdfa and opt.cross_doc_link_action == "1":
                raise ValidationError(
                    _(
                        "The PDF/A option is not compatible with "
                        "'Cross-document Links' = "
                        "'Open with PDF Reader Application'."
                    )
                )
            if opt.magnification == "4" and (opt.zoom < 50 or opt.zoom > 1600):
                raise ValidationError(
                    _(
                        "The value of the zoom factor must be between 50 and 1600 "
                        "(current value: %d)"
                    )
                    % opt.zoom
                )

    @api.onchange("encrypt")
    def encrypt_change(self):
        if not self.encrypt:
            self.document_password = False

    @api.onchange("restrict_permissions")
    def restrict_permissions_change(self):
        if not self.restrict_permissions:
            self.permission_password = False

    @api.onchange("pdfa")
    def pdfa_change(self):
        if self.pdfa:
            self.pdf_form = False
            self.encrypt = False
            self.restrict_permissions = False

    def odoo2libreoffice_options(self):
        self.ensure_one()
        options = {}
        # GENERAL TAB
        if self.image_compression == "lossless":
            options["UseLosslessCompression"] = True
        else:
            options["UseLosslessCompression"] = False
            options["Quality"] = self.image_jpeg_quality
        if self.image_reduce_resolution != "none":
            options["ReduceImageResolution"] = True
            options["MaxImageResolution"] = int(self.image_reduce_resolution)
        else:
            options["ReduceImageResolution"] = False
        if self.watermark and self.watermark_text:
            options["Watermark"] = self.watermark_text
        if self.pdfa:
            options["SelectPdfVersion"] = 1
            options["UseTaggedPDF"] = self.tagged_pdf
        else:
            options["SelectPdfVersion"] = 0
        if self.pdf_form and self.pdf_form_format and not self.pdfa:
            options["ExportFormFields"] = True
            options["FormsType"] = int(self.pdf_form_format)
            options["AllowDuplicateFieldNames"] = self.pdf_form_allow_duplicate
        else:
            options["ExportFormFields"] = False

        options.update(
            {
                "ExportBookmarks": self.export_bookmarks,
                "ExportPlaceholders": self.export_placeholders,
                "ExportNotes": self.export_comments,
                "ExportHiddenSlides": self.export_hidden_slides,
            }
        )

        # INITIAL VIEW TAB
        options.update(
            {
                "InitialView": int(self.initial_view),
                "InitialPage": self.initial_page,
                "Magnification": int(self.magnification),
                "PageLayout": int(self.page_layout),
            }
        )

        if self.magnification == "4":
            options["Zoom"] = self.zoom

        # USER INTERFACE TAB
        options.update(
            {
                "ResizeWindowToInitialPage": self.resize_windows_initial_page,
                "CenterWindow": self.center_window,
                "OpenInFullScreenMode": self.open_fullscreen,
                "DisplayPDFDocumentTitle": self.display_document_title,
                "HideViewerMenubar": self.hide_menubar,
                "HideViewerToolbar": self.hide_toolbar,
                "HideViewerWindowControls": self.hide_window_controls,
            }
        )

        if self.open_bookmark_levels:
            options["OpenBookmarkLevels"] = int(self.open_bookmark_levels)

        # LINKS TAB
        options.update(
            {
                "ExportBookmarksToPDFDestination": self.export_bookmarks_named_dest,
                "ConvertOOoTargetToPDFTarget": self.convert_doc_ref_to_pdf_target,
                "ExportLinksRelativeFsys": self.export_filesystem_urls,
                "PDFViewSelection": int(self.cross_doc_link_action),
            }
        )

        # SECURITY TAB
        if not self.pdfa:
            if self.encrypt and self.document_password:
                options["EncryptFile"] = True
                options["DocumentOpenPassword"] = self.document_password
            if self.restrict_permissions and self.permission_password:
                # fmt: off
                options.update(
                    {
                        "RestrictPermissions": True,
                        "PermissionPassword": self.permission_password,
                        "Printing": int(self.printing),
                        "Changes": int(self.changes),
                        "EnableCopyingOfContent": self.content_copying_allowed,
                        "EnableTextAccessForAccessibilityTools":
                            self.text_access_accessibility_tools_allowed,
                    }
                )
                # fmt: on

        logger.debug("Py3o PDF options ID %s converted to %s", self.id, options)
        return options
