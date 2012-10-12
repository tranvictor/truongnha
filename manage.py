#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    argvs = sys.argv
    print argvs
    if 'test' in argvs or 'tntest' in argvs:
        os.environ.setdefault("DJANGO_SETTINGS_TESTING", "True")
    if 'sqlitedumpdata' in argvs:
        os.environ.setdefault("DJANGO_SETTINGS_TESTING", "True")
        argvs[1] = 'dumpdata'
    if 'tntest' in argvs:
        print 'tag'
        argvs[1] = 'test'
        if len(argvs) >=4:
            cl_name = argvs[3]
            print cl_name
            os.environ.setdefault('DJANGO_CLASS_TESTING', cl_name)
            del argvs[3]
        print argvs
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(argvs)
