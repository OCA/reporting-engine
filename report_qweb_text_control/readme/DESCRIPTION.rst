Allow text reports to generate positional text files by providing 
precise control over whitespace, special characters, and field formatting.

Use Case
--------

Generate fixed-width text files for legacy systems, bank transfers, or any interface 
requiring exact positional formatting with specific characters and spacing.

Example
-------

Template::

    <span t-esc="A(partner.name, 20)"/>
    <span t-esc="N(partner.id, 10)"/>
    <span t-esc="M(partner.credit_limit, 12)"/>

Output::

    John Doe           00000012340000015000+
