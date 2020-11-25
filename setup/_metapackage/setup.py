import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-reporting-engine",
    description="Meta package for oca-reporting-engine Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-report_xlsx',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
    ]
)
