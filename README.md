lmms-midi
=========
A simple Python script to convert uncompressed (.mmp) LMMS songs to MIDI files, complete with instruments.  

## Installation and usage

First, make sure you have the latest version of Python. You can head over to https://python.org/downloads to get it.  
Then you just need to install all the program's requirements (which is just MIDIUtil):
```bash
pip install -r requirements.txt
```
Now you can run lmms-midi! Download it from either the Releases tab or, if I haven't released any versions yet, from the green "Code" drop-down. Here's some example usage for `main.py`:
```bash
python3 main.py YOURFILE.mmp
```

## What works (to my knowledge)

* SF2 players
    * Note velocity
    * Track panning
    * Track volume
* SF2 players in beat/bassline tracks
* SF2 drum kits (be sure to set the bank to 128)
* Pitch/volume/pan automation tracks

## What doesn't work (yet)
Help reduce this list to zero by contributing to lmms-midi! New issues and PRs are very welcome and encouraged!

* Track volume > 100%
* Track pitch
* Note panning
* Master volume automation tracks
* Automation tracks in beat/bassline tracks

## What can't work

* Track volume > 100%
   * Mostly due to how, with MIDIUtil, volumes for tracks are between 0 and 128. A 100% volume for a track in LMMS translates to 128, and you can't go over 128, so you can't have tracks with a volume greater than 100%. Instead, to make tracks louder, try increasing note velocities.

* Any instrument track that isn't an SF2 player (including audio samples)
   * Kind-of self-explanatory: you can't play custom synths with MIDI. Be warned though that SF2 files may have extra instruments that might not be standard throughout, so keep an eye out for your SF2 player's bank/patch.

## Notes

* Here's a useful link for some MIDI specifications: https://www.music.mcgill.ca/~ich/classes/mumt306/StandardMIDIfileformat.html
* If you have multiple drum tracks, they'll converge into one because you can only have one MIDI channel for drums. It'll sound fine, but this means the resulting drum track will take on the properties (ex. volume/panning) of the lowest drum track you have (where beat/bassline tracks count as lower than regular tracks). Unfortunately this also means that LMMS, when importing your .mid files, will also import the drums as one track.
