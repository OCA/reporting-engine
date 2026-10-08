This module allows you to add positioned images (such as watermarks, logos,
or stamps) to PDF reports. Images can be precisely positioned using millimeter
coordinates (top, left) and you can control whether they appear on all pages
or only the first page.

The module supports two types of images:

- *Company-level Images*: Define images at the company level that can be
  included in reports by enabling the *Include Company Images* option
- *Report-specific Images*: Configure specific images for individual reports,
  filtered by company context and always shown when configured

Images can be assigned to a specific company or left as shared records
(without company assignment) for use across multiple companies

An image can also be made *conditional* by giving it a domain: it is then
printed only on the records matching that domain. This is how one report can
carry, say, a signature stamp for some customers and not for others. The domain
is evaluated against the model of the report being printed, so a single image
can guard several reports.
