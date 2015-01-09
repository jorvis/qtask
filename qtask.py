#!/usr/bin/env python3

"""
For full command info and documentation please see the GitHub project page here:

https://github.com/jorvis/qtask

What follows are just development notes.

............................................
Example commands supported:

    qtask init
 
    qtask add project annotation
 
    qtask log "Conference call with review panel"
    qtask log "Added parsing script for latest version of tool X" to annotation
    qtask log 5 hours against task 231

    qtask list projects
    qtask list annotation work
    qtask list work in last 30 days
    qtask list annotation work in last 1 week

    qtask help log

"""

import argparse
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

        if command == 'log':
            if len(args.arglist) < 2:
                print_error("Usage: qtask log <description>.  Please see help for more examples")
            else:
                process_log_command(curs, args.arglist)

        elif command == 'list':
            print_error("Qtask: Sorry, the list command is not yet implemented")

        elif command == 'add':
            if len(args.arglist) != 3:
                print_error("Usage: qtask add project <foo>")
            else:
                process_add_command(curs, args.arglist[1], args.arglist[2])

        elif command == 'help':
            if len(args.arglist) != 2:
                print_error("Usage: qtask help <somecommand>")
            else:
                print_help_for_command(args.arglist[1])

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

    else:
        print_error("Qtask: Sorry, help for the command ({0}) is not yet implemented".format(cmd))

        
def process_add_command(curs, item_type, label):
    print("Attempting to insert project: {0}".format(label))
    if item_type == 'project':
        curs.execute("INSERT INTO project (label, time_added) VALUES (?, datetime('now'))", (label,) )
        row_id = curs.lastrowid
        print("Qtask: Project '{0}' added to the database with id={1}".format(label, row_id))
        return row_id
    else:
        print_error("Qtask: Sorry, there is currently only support for adding projects")


def process_log_command(curs, args):
    # get rid of the first argument, which was just the 'log' command
    args.pop(0)
    
    # There are several different ways to call this.
    # 1 argument:  Must be a label only, no project association
    if len(args) == 1:
        curs.execute("INSERT INTO task (label, time_added) VALUES (?, datetime('now'))", (args[0],) )
        print("Qtask: task id:{0} logged".format(curs.lastrowid))

    # 3 arguments:  <label> to <project>
    elif len(args) == 3 and args[1] == 'to':
        project_label = args[2]
        project_id = get_project_id_by_label(curs, project_label)

        if project_id is None:
            pass
        else:
            curs.execute("INSERT INTO task (label, time_added, project_id) VALUES (?, datetime('now'), ?)",
                         (args[0], project_id) )
            print("Qtask: task id:{0} logged to project {1}".format(curs.lastrowid, project_label))

    # 5 elements, like: 5 hours against task 231
    elif len(args) == 5 and args[2] == 'against':
        print_error("Sorry, logging time against a task isn't yet implemented.")

    else:
        print_error("Qtask: I didn't understand your log command.  See 'qtask help log' for examples")

if __name__ == '__main__':
    main()







