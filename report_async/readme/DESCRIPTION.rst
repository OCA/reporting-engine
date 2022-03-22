The new menu "Report Center" is the central place to host your reports in one place.
From here, there are 2 ways to launch the report,

1. Run Now - run report immediately as per normal.
2. Run Background - put the report execution to queue job.

There are additional settings under *Reports* -> *Async Options* for specific reports using async options:

- Async report - Whether the report should be async.
- Min of Records - How many records required to trigger async reports.
- Mail Recipient - This by defualt is the logged in user's email, but can be reconfigured in a popup dialog.

By using the queue job, option 2 is great for long running report.
The report file will be saved for later use, with the option to send report
by email as soon as it is ready.

Notes:

* Only user with Technical Feature rights can manage the report.
* Every internal user will have right to execute the report allowed for his/her groups.
* The files created are owned and viewable only by the person who run the report.
* Job queue manager can also see all jobs for each reports.
