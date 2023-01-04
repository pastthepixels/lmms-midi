#!/usr/bin/python3
from lmms_midi import set_wizard_mode, parse_xml
from xml.etree.ElementTree import ParseError
import sys, os

HELP_TEXT ="""
lmms-midi
=========
USAGE:
    main.py FILENAME.mmp
FLAGS:
    --debug   --> Shows IndexError and FileNotFoundError errors instead of assuming you did something wrong
    --help    --> Shows this screen
    --wizard  --> Ask about things like whether to include non-SF2 tracks
"""

debug = False
files = []

def export_all():
    if files == []:
        print(HELP_TEXT)
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
            
            case "--wizard":
                set_wizard_mode(True)

            case _:
                files.append(str(sys.argv[i]))

find_flags()

if debug:
    export_all()
else:
    try:
        export_all()
    except (FileNotFoundError, ParseError) as err:
        print("Something went wrong! Check your file path and make sure it ends in '.mmp' or run with --debug.")
    except:
        print("Something went wrong! Run with --debug for more info.")
