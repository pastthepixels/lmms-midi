lmms-midi
=========
A simple Python script to convert uncompressed (.mmp) LMMS songs to MIDI files, complete with instruments.  
*Note: The way this works means that it will only work for SF2 players.*

USAGE
=====
Installing all requirements (which is just MIDIUtil):
```bash
pip install -r requirements.txt
```
With `main.py`:
```bash
python3 main.py YOURFILE.mmp
```

What doesn't work (yet)
=======================
* Beat/Bassline editor
* Multiple drum tracks
* Effects (incl. reverb/chorus)
* Automation
* Track volume > 100%

*Useful link for some MIDI specifications: https://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html*

What does work (to my knowledge)
================================
Everything else
