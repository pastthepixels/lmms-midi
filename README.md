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
* Effects (incl. reverb/chorus)
* Automation
* Track volume > 100%

*Useful link for some MIDI specifications: https://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html*

What does work (to my knowledge)
================================
Everything else

Notes
=====
* If you have multiple drum tracks, they'll converge into one because you can only have one MIDI channel for drums. It'll sound fine, but this means the resulting drum track will take on the properties (ex. volume/panning) of the lowest drum track you have (where beat/bassline tracks count as lower than regular tracks). Unfortunately this also means that LMMS, when importing your .mid files, will also import the drums as one track.
