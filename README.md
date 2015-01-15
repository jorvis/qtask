## Overview

I created Qtask to quickly record work/tasks I have done (or need to) from the command line, group them based on project, and easily generate reports.  Most parts are optional, but each element recorded has an ID, label, a datestamp, time committed, and associated project.

The entries themselves are stored in a SQLite3 database (nothing fancy, just a file on disk.)


## Usage

I tried to make the usage follow natural language as much as possible rather than use a lot of command-line switches.

First, initialize Qtask:

```
    qtask init
```

Optionally, create a project:

```
    qtask add project Annotation
```

Record work done, a meeting, whatever:

```
    qtask log "Conference call with review panel"
```

Or, if you want to link the task to a project when you log it:

```
    qtask log "Added parsing script for latest version of tool X" to Annotation
```

If you're interested in actually logging time rather than just lists of work you
can do that too.  When you log new work you'll get a task ID reported back on the
command line for it.  To actually log hours against that, you can do it like this:

```
qtask log 5 hours against task 231
```

If you don't know the ID, they are always displayed when listing work.

### Listing things

Show the projects you've added

```
    qtask list projects
```

List all work for a project (most recent first)

```
    qtask list Annotation work
```

You can also do time intervals (deltas)

```
    qtask list work in last 30 days
```

And, of course, limit these by project too

```
    qtask list Annotation work in last 2 weeks
```

### Generating reports (graphics)

Nothing here yet


## Help

Get help on any command by using help, then the command name, such as:

```
qtask help init
```


## Getting the code

The best way to get the code for now is to just clone it:

```
    git clone https://github.com/jorvis/qtask.git
```

Or you can get a zip file of the most current code at:

```
    https://github.com/jorvis/qtask/archive/master.zip
```

## Problems?

If you encounter any issues or have suggestions,  please submit to the [Issue tracking system](https://github.com/jorvis/qtask/issues)


Contributing
============

I welcome contributions, either in the form of code (pull requests) or suggestions submitted to the [tracker](https://github.com/jorvis/qtask/issues).
