Menu: Dashboard > Report Center

As Technical Feature users, you can manage reports for Report Center.

- **Report:** choose the report (a window action). Although the option show all window actions
  it only make sense for window actions that launch reports.
- **Allow Async:** check this, if you want the report to run in background too, suitable for
  report that return file as result, i.e., pdf/xlsx/csv/txt.
- **Email Notification:** if checked, once the background process is completed, email with link to download
  report will be sent.
- **Groups:** select user groups allowed to use this report. If left blank, all user can use.

As normal user, you can run your reports from Report Center

- **Run Now button:** to run report immediately as per normal.
- **Run Background button:** to run report asynchronously. Fall back to run now, if not report that produce file.
- **Job Status:** show status of the latest run job. If job fail, exception error will also shown
- **Files:** show all files being produced by the job as run by the user.
- **Jobs:** show all jobs triggered by this report as run by the user. Only job queue manager have access to this button.
