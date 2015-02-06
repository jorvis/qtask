#!/usr/bin/env python3

"""
For full command info and documentation please see the GitHub project page here:

https://github.com/jorvis/qtask

You can also use the help command to get documentation for any individual command:

qtask help

or

qtask help add

WARNINGS:
For any time deltas based on a 'year', 365 days are used.

"""

import argparse
import datetime
import os
import sqlite3
import sys

def main():
    DB_FILE_PATH = "{0}/.qtask.db".format(os.environ['HOME'])
    
    parser = argparse.ArgumentParser( description='Command-line task logging, management and reporting')
    parser.add_argument('arglist', metavar='N', type=str, nargs='+', help='All arguments to qtask to here.')
    args = parser.parse_args()

    command = args.arglist[0]
    
    if command == 'init':
        initialize_db(DB_FILE_PATH)

    else:
        # this creates it if it doesn't already exist
        conn = sqlite3.connect(DB_FILE_PATH)
        curs = conn.cursor()

        if command == 'add':
            if len(args.arglist) != 3:
                print_error("Usage: qtask add project <foo>")
            else:
                process_add_command(curs, args.arglist[1], args.arglist[2])

        elif command == 'help':
            if len(args.arglist) == 1:
                print("Qtask help:  Get help by passing any command name 'add', 'log', 'list', or 'init'.  For example:\n\n" \
                      "\tqtask help add\n")
            elif len(args.arglist) == 2:
                print_help_for_command(args.arglist[1])
            else:
                print_error("Usage: qtask help <somecommand>")

        elif command == 'list':
            if len(args.arglist) < 2:
                print_error("Usage: qtask list <description>.  Please see help for more examples")
            else:
                process_list_command(curs, args.arglist)
                
        elif command == 'log':
            if len(args.arglist) < 2:
                print_error("Usage: qtask log <description>.  Please see help for more examples")
            else:
                process_log_command(curs, args.arglist)

        elif command == 'report':
            if len(args.arglist) == 6:
                process_report_command(curs, args.arglist)
            else:
                print_error("Usage: qtask report work in last <N> <units>.  Please see help for more examples")

        else:
            raise Exception("ERROR: Unrecognized qtask command: {0}".format(command))

        conn.commit()
        curs.close()


def get_project_id_by_label(curs, label):
    curs.execute('''SELECT id FROM project WHERE label=?''', (label,) )
    row = curs.fetchone()
        
    if row:
        return row[0]
    else:
        return None


def initialize_db(file_path):
    # First, check to see if the file exists already.
    if os.path.exists(file_path):
        # Don't stomp the existing file.
        print("\nWARNING: init command called but the db file ({0}) already exists.  Cowardly refusing " \
              "to stomp over it.  If you want to re-initialize your database, please delete that file " \
              "first and run the init command again.\n".format(file_path))
        sys.exit(1)

    conn = sqlite3.connect(file_path)
    curs = conn.cursor()

    curs.execute("""
              CREATE TABLE project (
                 id                integer primary key autoincrement,
                 label             text,
                 time_added        text
              )
    """)
    
    curs.execute("""
              CREATE TABLE task (
                 id                integer primary key autoincrement,
                 parent_id         integer,
                 label             text,
                 time_added        text,
                 time_logged       real,
                 project_id        integer,
                 FOREIGN KEY(project_id) REFERENCES project(id)
              )
    """)

    curs.execute("CREATE INDEX idx_task_parent_id ON task (parent_id)")
    curs.execute("CREATE INDEX idx_task_time_added ON task (time_added)")

    conn.commit()
    curs.close()

def list_tasks(curs, project_id=None, from_date=None, until=None):
    qry_args = list()
    qry_str = '''
    SELECT t.label AS task_label, t.time_added, t.time_logged, p.label AS project_name
      FROM task t
           LEFT JOIN project p ON t.project_id=p.id
    '''

    if project_id is not None:
        qry_str += " WHERE p.id = ? "
        qry_args.append(project_id)

    if from_date is not None:
        qry_str += " WHERE t.time_added BETWEEN ? AND ? "
        qry_args.append(from_date)
        qry_args.append(until)

    qry_str += " ORDER BY t.time_added DESC "

    #print("QRY: {0}, ARGS: {1}".format(qry_str, qry_args))
    
    curs.execute(qry_str, (qry_args) )
    work_count = 0

    print("# Work logged\n# -----------")
    for (task_label, time_added, time_logged, project_name) in curs:
        work_count += 1
        print("{0}\t{1}\t{2}\t{3}".format(project_name, time_added, time_logged, task_label))

    if work_count == 0:
        print("#- No work logged -#")

    
def print_error(msg):
    print(msg)
    sys.exit(1)

    
def print_help_for_command(cmd):
    if cmd == 'init':
        print("""
        Qtask help command: init
        
        This command initializes a user-specific Qtask database (SQLite3) by setting up the 
        tables necessary to store its data.  This creates a hidden file called '.qtask.db'
        in your home area, as defined by the HOME environmental variable.  If the file 
        already exists, Qtask will report an error and leave it untouched.
        """)

    elif cmd == 'add':
        print("""
        Qtask help command: add
        
        The 'add' command is an administrative one, currently only used to add new projects
        to the database against which work can be logged.

        Example usage:

           qtask add project 'T. parva'
           qtask add project rna_seq

        If your project name contains spaces or special characters, you should sound it with
        quotation marks.
        """)

    elif cmd == 'help':
        print("""
        Qtask help command: help
        
        Looking for help on the help command itself?  You recursively sly devil.  

        If you run the help command on its own, you'll get a list of available help commands:

           qtask help

        Pass the name of a command to get documentation on it:

           qtask help log
           qtask help add

        """)

    elif cmd == 'log':
        print("""
        Qtask help command: log
        
        The 'log' command is used to record tasks performed.  The basic usage is to just provide a
        label, which will be stored along with the current date/time.  You can expand upon this by
        logging the task to a specific project by the project's label.  You can also log additional
        time to an already-existent task.

        Example usage:

           qtask log "Installed latest version of BLAST"
           qtask log "Created JBrowse instance" to Annotation
           qtask log "Submitted timesheets" on 2015-01-13
           qtask log "Created bowtie2 index of genomes" to Annotation on 2015-01-21
           qtask log 5 hours against task 231

        """)

    elif cmd == 'list':
        print("""
        Qtask help command: list
        
        The 'list' command is used to display things stored in the database such as projects or
        work.  You can list things generally such as all work (by default) or describe specific
        filtering criteria in a natural syntax.  Probably easiest with examples:

        Example usage:

            qtask list projects
            qtask list work
            qtask list work today
            qtask list Annotation work
            qtask list work in last 30 days
            qtask list Annotation work in last 1 week

        """)

    elif cmd == 'report':
        print("""
        Qtask help command: report
        
        The 'report' command is used group and display work logged by project over a given time
        interval.

        Example usage:

            qtask report work in last 30 days
            qtask report work in last 1 week
        
        """)
        
    else:
        print_error("Qtask: Sorry, help for the command ({0}) is not yet implemented".format(cmd))

        
def process_add_command(curs, item_type, label):
    print("Attempting to insert project: {0}".format(label))
    now = "{0}".format(datetime.datetime.now())
    
    # parsing wouldn't work if any of these words were used as a project name
    project_reserved_words = ['work']
    
    if item_type == 'project':
        if label in project_reserved_words:
            print_error("Qtask: Sorry, the word '{0}' is reserved and can't be used for a project name.".format(label))
        
        curs.execute("INSERT INTO project (label, time_added) VALUES (?, ?)", (label, now) )
        row_id = curs.lastrowid
        print("Qtask: Project '{0}' added to the database with id={1}".format(label, row_id))
        return row_id
    else:
        print_error("Qtask: Sorry, there is currently only support for adding projects")

def process_list_command(curs, args):
    # get rid of the first argument, which was just the 'list' command
    args.pop(0)
    now = datetime.datetime.now()

    # There are several different ways to call this.
    # 1 argument: Currently only supports direct lists of 'projects' or 'work'
    if len(args) == 1:
        if args[0] == 'projects':
            curs.execute('''SELECT id, label, time_added FROM project ORDER BY LABEL''' )
            project_count = 0

            print("# Projects\n# --------")
            for (id, label, time_added) in curs:
                print("{0}\t{1}".format(label, time_added))
                project_count += 1

            if project_count == 0:
                print("#- No projects found -#")
            
        elif args[0] == 'work':
            list_tasks(curs)

        else:
            print_error("Qtask: Sorry, I don't know how to list {0}".format(args[0]))

    # examples of two arguments
    #   qtask list Annotation work
    elif len(args) == 2:
        # if the 2nd term is 'work' the first is assumed to be the project
        if args[1] == 'work':
            project_id = get_project_id_by_label(curs, args[0])
            if project_id is None:
                print_error("Qtask.  Couldn't list work in project {0} because the project wasn't found.".format(args[0]))
            else:
                list_tasks(curs, project_id=project_id)

        # if the 1st term is 'work' the following is chronological description.  E.g:
        #  qtask list work today
        elif args[0] == 'work':
            if args[1] == 'today':
                from_date = "{0} 00:00:00".format(datetime.date.today())
                until_date = "{0}".format(datetime.datetime.now())
                list_tasks(curs, from_date=from_date, until=until_date)
            else:
                print_error("Qtask: Sorry, I couldn't recognize your list syntax. Please see the examples and try again")
        else:
            print_error("Qtask: Sorry, I couldn't recognize your list syntax. Please see the examples and try again")

    # examples of four arguments
    #  qtask list work in last 30 days
    #  qtask list work in last 1 week
    elif len(args) == 5:
        if args[1] == 'in' and args[2] == 'last':
            delta = get_delta(int(args[3]), args[4])

            if delta == None:
                print_error("Qtask: Sorry, I couldn't recognize your list syntax. Please see the examples and try again")
            
            list_tasks(curs, from_date="{0}".format(now - delta), until=str(now))
        else:
            print_error("Qtask: Sorry, I couldn't recognize your list syntax. Please see the examples and try again")


def process_log_command(curs, args):
    # get rid of the first argument, which was just the 'log' command
    args.pop(0)
    now = "{0}".format(datetime.datetime.now())
    
    # There are several different ways to call this.
    # 1 argument:  Must be a label only, no project association
    if len(args) == 1:
        curs.execute("INSERT INTO task (label, time_added) VALUES (?, ?)", (args[0], now) )
        print("Qtask: task id:{0} logged".format(curs.lastrowid))

    # 3 arguments:  <label> to <project>
    elif len(args) == 3 and args[1] == 'to':
        project_label = args[2]
        project_id = get_project_id_by_label(curs, project_label)

        if project_id is None:
            print_error("Qtask: ERROR: couldn't find project '{0}' to log work against".format(project_label))
        else:
            curs.execute("INSERT INTO task (label, time_added, project_id) VALUES (?, ?, ?)",
                         (args[0], now, project_id) )
            print("Qtask: task id:{0} logged to project {1}".format(curs.lastrowid, project_label))

    # 3 arguments, like: "Submitted timesheets" on 2015-01-13
    elif len(args) == 3 and args[1] == 'on':
        curs.execute("INSERT INTO task (label, time_added) VALUES (?, datetime(?))", (args[0],args[2]) )
        print("Qtask: task id:{0} logged".format(curs.lastrowid))
            
    # 5 elements, like: 5 hours against task 231
    elif len(args) == 5 and args[2] == 'against':
        print_error("Sorry, logging time against a task isn't yet implemented.")

    # 5 elements, like: "Created bowtie2 index of genomes" to Annotation on 2015-01-21
    elif len(args) == 5 and args[1] == 'to' and args[3] == 'on':
        project_label = args[2]
        project_id = get_project_id_by_label(curs, project_label)

        if project_id is None:
            print_error("Qtask: ERROR: couldn't find project '{0}' to log work against".format(project_label))
        else:
            curs.execute("INSERT INTO task (label, time_added, project_id) VALUES (?, ?, ?)",
                         (args[0], args[4], project_id) )
            print("Qtask: task id:{0} logged to project {1} on {2}".format(curs.lastrowid, project_label, args[4]))

    # 5 elements, like: "Created bowtie2 index of genomes" on 2015-01-21 to Annotation
    elif len(args) == 5 and args[3] == 'to' and args[1] == 'on':
        project_label = args[4]
        project_id = get_project_id_by_label(curs, project_label)

        if project_id is None:
            print_error("Qtask: ERROR: couldn't find project '{0}' to log work against".format(project_label))
        else:
            curs.execute("INSERT INTO task (label, time_added, project_id) VALUES (?, ?, ?)",
                         (args[0], args[2], project_id) )
            print("Qtask: task id:{0} logged to project {1} on {2}".format(curs.lastrowid, project_label, args[2]))

    else:
        print_error("Qtask: I didn't understand your log command.  See 'qtask help log' for examples")

def process_report_command(curs, args):
    # get rid of the first argument, which was just the 'report' command
    args.pop(0)
    now = datetime.datetime.now()

    # example: qtask report work in last 30 days
    if args[0] == 'work':
        if args[1] == 'in' and args[2] == 'last':
            delta = get_delta(int(args[3]), args[4])

            if delta == None:
                print_error("Qtask: Sorry, I couldn't recognize your report syntax. Please see the examples and try again")

            from_date = "{0}".format(now - delta)
            until = str(now)

            qry_str = '''
            SELECT t.label AS task_label, t.time_added, t.time_logged, p.label AS project_name
              FROM task t
                   LEFT JOIN project p ON t.project_id=p.id
                   WHERE t.time_added BETWEEN ? AND ? 
            '''
            curs.execute(qry_str, (from_date, until) )

            projects = dict()

            for (task_label, time_added, time_logged, project_name) in curs:
                # 'None' doesn't work well
                if project_name is None:
                    project_name = 'Unassigned to a project'
                
                if project_name not in projects:
                    projects[project_name] = list()

                projects[project_name].append({'task_label': task_label, 'time_added': time_added})

            for project_label in projects:
                print("{0}".format(project_label))

                for task in projects[project_label]:
                    print("- {0}".format(task['task_label']))
            
        else:
            print_error("Qtask: Sorry, I couldn't recognize your list syntax. Please see the examples and try again")
    else:
        report_error("Qtask: ERROR: I didn't understand your report command.  See 'qtask help report' for examples")

def get_delta(quant, unit):
    """
    Returns a delta based on a given quantity and unit.  Valid units are:

    day, days, week, weeks, year, years
    """
    delta = None

    if unit == 'day' or unit == 'days':
        delta = datetime.timedelta(days=quant)
    elif unit == 'week' or unit == 'weeks':
        delta = datetime.timedelta(weeks=quant)
    elif unit == 'month' or unit == 'months':
        # Someone offer a clean way to support this?
        print_error("Qtask: Sorry, can't display 'months', because it is imprecise.  Please try a specific number of weeks instead")
    elif unit == 'year' or unit == 'years':
        # python's module doesn't support years as imprecise.  Instead, we'll assume year=365 days
        quant = quant * 365
        delta = datetime.timedelta(days=quant)

    return delta

if __name__ == '__main__':
    main()







