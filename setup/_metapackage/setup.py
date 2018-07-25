import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo10-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo10-addon-bi_sql_editor',
        'odoo10-addon-bi_view_editor',
        'odoo10-addon-report_py3o',
        'odoo10-addon-report_py3o_fusion_server',
        'odoo10-addon-report_qweb_element_page_visibility',
        'odoo10-addon-report_qweb_parameter',
        'odoo10-addon-report_qweb_pdf_watermark',
        'odoo10-addon-report_qweb_signer',
        'odoo10-addon-report_qweb_txt',
        'odoo10-addon-report_wkhtmltopdf_param',
        'odoo10-addon-report_xlsx',
        'odoo10-addon-report_xml',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
