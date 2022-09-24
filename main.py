#!/usr/bin/python3
from lmms_midi import *
import sys

try:
    for i in range(1, len(sys.argv)):
    	print(sys.argv[i])
    	parse_xml(str(sys.argv[i])).compile_export()
except (IndexError, FileNotFoundError) as err:
    print("lmms-midi\n=========\nUSAGE:\n\tmain.py FILENAME.mmp")