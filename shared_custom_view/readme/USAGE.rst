To use this module, you should:

* create a configure a dashboard to your liking in the usual way
* in Settings / Technical / User Interface / Views, find the My Dashboard view and duplicate it. Save the duplicated view after changing its name. We will use "Shared Dashboard View" in the rest of this page.
* in Settings / Technical / Actions / Windows Actions, find the "My Dashboard" action and duplicate it. Give it a new name (don't forget the translations). We will use "Shared Dashboard Action" in the rest of this page. Possibly set some security rules. Set the "View Ref" field to "Shared Dashboard View".
* in Settings / Technical / User Interface / Menu Items, find the "My Dashboard" menu item and duplicate it (don't forget the tranlations). We will use "Shared Dashboard" in the rest of this page. Set the action to "Shared Dashboard Action".
* in Settings / Technical / User Interface / Customize Views, find the last dashboard created with your user and edit it: set the view to "Shared Dashboard View" and remove the User

Refresh your browser session to update the view cache. Test that you can access the new dashboard with your user or with any user having the groups set in the security of the action.
