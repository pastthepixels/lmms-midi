# !/bin/bash
# Requires the "patch" command -- you can install it on Fedora with `sudo dnf install patch`
# https://github.com/MarkCWirt/MIDIUtil/issues/24#issuecomment-586261611
find ~/.local/lib/ -name "MidiFile.py" -exec patch {} patch-issue-24.patch \;
