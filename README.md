lmms-midi
=========
A simple Python script to convert uncompressed (.mmp) LMMS songs to MIDI files, complete with instruments.  

## Installation and usage

First, make sure you have the latest version of Python. You can head over to https://python.org/downloads to get it.  
Then you just need to install all the program's requirements (which is just MIDIUtil):
```bash
pip install -r requirements.txt
```
Now you can run lmms-midi! Here's some example usage for `main.py`:
```bash
python3 main.py YOURFILE.mmp
```

## What works (to my knowledge)

* SF2 players (but -- and intentionally -- not other kinds of instruments as they can't be played back via MIDI)
    * Note velocity
    * Track panning
    * Track volume
* SF2 players in beat/bassline tracks
* SF2 drum kits (be sure to set the bank to 128)
* Pitch/volume/pan automation tracks

## What doesn't work (yet)

* Track volume > 100%
* Track pitch
* Note panning
* Master volume automation tracks
* Automation tracks in beat/bassline tracks
* Multiple beat/bassline tracks

Help reduce this list to zero by contributing to lmms-midi! New issues and PRs are very welcome and encouraged!

*Useful link for some MIDI specifications: https://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html*

## Notes

* If you have multiple drum tracks, they'll converge into one because you can only have one MIDI channel for drums. It'll sound fine, but this means the resulting drum track will take on the properties (ex. volume/panning) of the lowest drum track you have (where beat/bassline tracks count as lower than regular tracks). Unfortunately this also means that LMMS, when importing your .mid files, will also import the drums as one track.


