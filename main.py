#!/usr/bin/python3
from lmms_midi import *
import sys

try:
    parse_xml(str(sys.argv[1])).compile_export()
except (IndexError, FileNotFoundError) as err:
    print("lmms-midi\n=========\nUSAGE:\n\tmain.py FILENAME.mmp")