import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-bi_sql_editor',
        'odoo12-addon-report_xlsx',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
