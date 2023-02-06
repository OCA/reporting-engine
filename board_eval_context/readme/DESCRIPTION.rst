This module adds some useful keys in the evaluation context of board.board
records, which can be useful when creating generic boards for all the users of
an instance.

At the moment it allows using the following values in the domains of a board.board record:

* datetime: the datetime.datetime class
* date: the datetime.date class
* timedelta: the datetime.timedelta class
* timezone: the datetime.timezone class
* tzinfo: the datetime.tzinfo class
* relativedelta: the dateutil.relativedelta.relativedelta class
* uid: the ID of the current user
