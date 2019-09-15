To use this module functionality you just need to:

On ``project.project`` level:

In Kanban View:

#. Go to Project > Dashboard
#. Create
#. Enter project name and use auto generated key or simply override value by entering your own key value.

In Tree View:

#. Go to Project > Configuration > Projects
#. Create
#. Enter project name and use auto generated key or simply override value by entering your own key value.

In form View:

#. Go to Project > Dashboard
#. Open the projects settings
#. Modify the "key" value
#. After modifying project key the key of any existing tasks related to that project will be updated automatically.

When you create a project, under the hood a ir.sequence record gets creted with prefix: ``<project-key>-``.

On ``project.task`` level:

#. Actually there is nothing to be done here
#. Task keys are auto generated based on project key value with per project auto incremented number (i.e. PA-1, PA-2, etc)

In browser address bar:

#. Navigate to your project by entering following url: http://<<your-domain>>/projects/PROJECT-KEY
#. Navigate to your task by entering following url: http://<<your-domain>>/tasks/TASK-KEY
