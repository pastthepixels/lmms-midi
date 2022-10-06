#!/usr/bin/python3
from lmms_midi import *
import sys, os

debug = False
files = []

def export_all():
    for path in files:
    	print("Exporting {0}...".format(path))
    	parse_xml(path).compile_export()

def find_flags():
    global debug
    global files
    for i in range(1, len(sys.argv)):
        match sys.argv[i]:
            case "--debug":
                debug = True

            case "--help":
                help()
                os._exit(0)

            case _:
                files.append(str(sys.argv[i]))

def help():
    print("lmms-midi\n=========\nUSAGE:\n\tmain.py FILENAME.mmp\nFLAGS:")
    print("\t--debug   --> Shows IndexError and FileNotFoundError errors instead of assuming you did something wrong")
    print("\t--help    --> Shows this screen")

find_flags()

if debug:
    export_all()
else:
    try:
        export_all()
    except (IndexError, FileNotFoundError) as err:
        help()
