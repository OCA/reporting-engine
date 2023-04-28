In order to start signing PDF documents you need to configure certificate(s)
to use in your company.

* Go to ``Settings > Companies > Companies > Your company``
* Go to ``Report configuration`` tab
* Click ``Edit``
* Add a new item in ``PDF report certificates`` list
* Click ``Create``
* Set name, certificate file, password file and model
* Optionally you can set a domain and filename pattern for saving as attachment

For example, if you want to sign only customer invoices in posted state:

* Model: ``account.move``
* Domain: ``[('move_type','=','out_invoice'), ('state', '=', 'posted')]``
* Save as attachment: ``(object.name or '').replace('/','_') + '.signed.pdf'``

**Note**: Linux user that executes Odoo server process must have
read access to certificate file and password file

Java Memory Settings
~~~~~~~~~~~~~~~~~~~~

If you are signing large amounts of reports at the same time, or if you have a
lower worker memory size than the JVM defaults, you may need to tune the JVM
heap memory limits. Do so by adding a ``$JVM_ARGS`` environment variable that
contains the required flags. Check out these links too:

- `StackOverflow answer <https://stackoverflow.com/a/14763095/1468388>`_.
- `Java docs <https://docs.oracle.com/cd/E15523_01/web.1111/e13814/jvm_tuning.htm#PERFM161>`_.
