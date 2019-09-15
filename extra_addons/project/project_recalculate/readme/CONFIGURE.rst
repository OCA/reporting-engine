You can define working calendar at Setting > Technical > Resource > Working time.
Then assign this calendar to a resource (related with a user), a project or
a company.

When calculating task dates, this addon will look for a working calendar in this order:

* If project has working time assigned, use it.
* If user assigned, search first resource related with this user
  (normally user is related, only with one resource) and get its working calendar
  ends at 18:00
* If not user assigned or resource hasn't working calendar, search first
  working calendar of the company
* If no working calendar found, then every day is workable and work starts at
  08:00 and ends at 18:00

Also you can define which task stages are included in recalculation when
'Project recalculate' button is clicked. By default, all are included.
To change this go to Project > Configuration > Stages > Task Stages and change
the 'Include in project recalculate' field.
