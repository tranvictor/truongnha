#!/usr/bin/env python
import os, sys

if __name__ == "__main__":
    argvs = sys.argv
    if 'test' in argvs:
        os.environ.setdefault("DJANGO_SETTINGS_TESTING", "True")
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
