To configure company-level images:

1.  Go to *Settings / Companies*
2.  Open your company record
3.  Navigate to the *Report Images* tab
4.  Add images with position settings:
    - Upload an image - width defaults to 50mm and height is automatically
      calculated to maintain the original aspect ratio
    - *Top (mm)*: Distance from the top of the page
    - *Left (mm)*: Distance from the left edge of the page
    - *Width (mm)*: Width of the image (changing this auto-adjusts height)
    - *Height (mm)*: Height of the image (changing this auto-adjusts width)
    - *Respect Image Ratio*: When enabled (default), changing width or height
      automatically adjusts the other dimension to maintain aspect ratio.
      Uncheck for manual control of both dimensions.
    - *First Page Only*: Check to show only on the first page
    - *Company*: Automatically set to the current company when creating from
      the company form. To create shared images, leave empty.

To configure report-specific images:

1.  Go to *Settings / Technical / Actions / Reports*
2.  Open the report you want to customize
3.  Navigate to the *Report Images* tab
4.  Check *Include Company Images* if you want to show company-level images
    in addition to report-specific images
5.  Add report-specific images in the list with the same position settings
    as above

**Note**: By default, images maintain their aspect ratio. When you upload an
image, it's automatically sized to 50mm width with proportional height. You can
then adjust either dimension and the other will update automatically to prevent
distortion.

To show an image on some records only:

1.  Open the image in the report's or the company's *Report Images* tab
2.  Fill in *Condition* with a domain selecting the records that should carry
    the image, for example `[('partner_id.country_id.code', '=', 'JP')]`

The condition is evaluated against whichever model the printed report renders,
so it is not tied to one report: the same image can guard an invoice, a
quotation and a delivery slip at once, as long as those models share the field
paths the domain uses. For an image on a report's *Report Images* tab, the domain
is checked against the model of every report the image is placed on, so a field
path that does not exist there is refused when you save. For an image on the
company's *Report Images* tab, the condition is only checked at print time.

**Note**: An image whose condition cannot be evaluated on the model being
printed is left out of that report rather than printed unguarded, and a warning
is logged.

**Note**: An image with a condition is printed only on reports whose layout
has a header for each record, such as `web.external_layout`. Reports without
one (e.g. built on `web.basic_layout`) leave it out.
