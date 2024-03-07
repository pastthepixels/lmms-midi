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
    --debug                     --> Shows IndexError and FileNotFoundError errors instead of assuming you did something wrong
    --help                      --> Shows this screen
    --output=/path/to/file.mid  --> Specify output file
    --wizard                    --> Ask about things like whether to include non-SF2 tracks
"""

debug = False
files = []
flags = [i.split("=") for i in sys.argv]
output = None

def export_all():
    if not files:
        print(HELP_TEXT)
    for path in files:
        if output:
            print(f"Using output file {output}:", end=" ")
        print(f"Exporting {path}...")
        parse_xml(path, output).compile_export()

def find_flags():
    for flag in flags:
        match flag[0]:
            case "--debug":
                globals()["debug"] = True

            case "--help":
                help()
                os._exit(0)
            
            case "--wizard":
                set_wizard_mode(True)

            case "--output":
                if len(flag) == 2:
                    globals()["output"] = flag[1]
                else:
                    print("Error: output file not specified.")
                    sys.exit(1)

            case _:
                if str(flag[0])[-4:] == ".mmp":
                    globals()["files"].append(str(flag[0]))

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
