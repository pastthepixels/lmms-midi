from array import ArrayType
from math import ceil, log2
import xml.etree.ElementTree as ET
from midiutil.MidiFile import MIDIFile

class Note:
    def __init__(self, pos:int=0, pan:float=0, length:int=1, vol:float=100, key:int=60):
        self.pitch = key
        self.time = pos
        self.duration = length
        self.volume = vol # out of 1, float
        self.pan = pan # WIP (it's the thought that counts)
    
    def clone(self):
        return Note(pos=self.time, pan=self.pan, length=self.duration, vol=self.volume, key=self.pitch)
    
    def to_string(self):
        return "Note: pitch={0}, time={1}, duration={2}, volume={3}, pan{4}".format(self.pitch, self.time, self.duration, self.volume, self.pan)

class Pattern:
    def __init__(self, pos:int, notes:ArrayType):
        self.pos = pos
        self.notes = notes
    
    def add_note(self, note:Note):
        self.notes.append(note)
    
    def to_string(self):
        string = "Pattern: "
        for idx, note in enumerate(self.notes):
            string += ("\n\t {0}. " + note.to_string()).format(idx)
        return string
    
    def get_length(self):
        return self.notes[-1].time + self.notes[-1].duration
    
    def clone_notes(self):
        notes = []
        for note in self.notes:
            notes.append(note.clone())
        return notes

class Track:
    patterns = []
    def __init__(self, name:str, bank:int=0, patch:int=0):
        self.patterns = []
        self.bank = bank
        self.patch = patch
        self.name = name
        self.volume = 0 # out of 1
        self.pan = 0 # -1 or 1
    
    def add_pattern(self, pattern:Pattern):
        self.patterns.append(pattern)

class Song:
    def __init__(self, name:str="", bpm:int=120, timesig:ArrayType=[4, 4]):
        self.timesig = timesig
        self.tracks = []
        self.name = name
        self.bpm = bpm
    
    def add_track(self, track:Track):
        self.tracks.append(track)

    def compile_export(self):
        midi_file = MIDIFile(len(self.tracks))
        channel = 0
        for track_num, track in enumerate(self.tracks):
            if channel == 9: channel += 1 # Skips ahead if on channel 9 without being set there
            oldchannel = channel
            if track.bank == 128: channel = 9 # Sets to channel 9 (drums) if bank is set to the one where there's drums
           
            midi_file.addTrackName(track_num, 0, track.name)
            midi_file.addTimeSignature(track_num, 0, self.timesig[0], int(log2(self.timesig[1])), 24)
            midi_file.addTempo(track_num, 0, self.bpm)
            midi_file.addProgramChange(track_num, channel, 0, track.patch) # Channel num (2nd variable) == track num
            midi_file.addControllerEvent(track_num, channel, 0, 7, min(int(track.volume * 255), 127)) # Sets the track's volume
            midi_file.addControllerEvent(track_num, channel, 0, 10, min(int((track.pan + 1) / 2 * 127), 127)) # Sets the track's pan

            for pattern in track.patterns:
                for note in pattern.notes:
                    note.pitch += 12 # Have to raise everything by an octave for some reason. Very cool
                    midi_file.addNote(track_num, channel, note.pitch, (note.time + pattern.pos) / 48, note.duration / 48, int(note.volume * 127))
            
            if track.bank == 128: channel = oldchannel # Restores channel count as usual
            channel += 1

        with open("{0}.mid".format(self.name), 'wb') as outf:
            midi_file.writeFile(outf)
    
    def get_measure_length(self):
        return self.timesig[1] * 48

def parse_xml(xml_path):
    # 1. Loads and parses XML
    tree = ET.parse(xml_path)
    root = tree.getroot()        
    # 2. Gets the <head> and <song> elements        
    head = root.find("head")
    song = root.find("song")
    # 3. Creates a Song instance with right name/bpm/time signature
    midi_song = Song(xml_path, int(head.attrib["bpm"]))
    midi_song.timesig = [int(head.attrib["timesig_numerator"]), int(head.attrib["timesig_denominator"])]
    # 4. Goes through each track, ensuring it's a SF2 Player
    sf2_tracks = []
    sf2_bb_tracks = []
    for track in song.find("trackcontainer"):
        if is_sf2_player(track):
            sf2_tracks.append(track)
        if track.find("bbtrack"):
            sf2_bb_tracks.append(track)
    # 5. Goes through each SF2 Player track
    for track in sf2_tracks:
        midi_track = midi_track_from_xml(track)
        # 6. Loops through each pattern, adding notes
        for pattern in track.findall("pattern"):
            midi_pattern = Pattern(pos=int(pattern.attrib["pos"]), notes=[])
            for note in pattern:
                midi_pattern.add_note(Note(pos=int(note.attrib["pos"]), pan=int(note.attrib["pan"]), length=int(note.attrib["len"]), vol=float(note.attrib["vol"]) / 200, key=int(note.attrib["key"])))
            midi_track.add_pattern(midi_pattern)
        # 7. Adds track
        midi_song.add_track(midi_track)
    # Easy, right? Well, just you wait until step 6...
    # 6. Goes through each SF2 Player Beat/Bassline track
    for bb_track in sf2_bb_tracks:
        # Goes over each "repeat", called a bbtco and I can't decipher what that stands for
        all_bbtco = []
        for child in bb_track:
            if child.tag == "bbtco" and child.attrib["muted"] == "0": all_bbtco.append([int(child.attrib["pos"]), int(child.attrib["len"])])
        # Goes over each individual track
        for track in bb_track.find("bbtrack/trackcontainer"):
            if is_sf2_player(track) == False: continue # <-- Not all sub-instruments will be sf2 players
            midi_track = midi_track_from_xml(track)
            # 6. Loops through each pattern, adding notes. Now THIS part is different...
            midi_patterns = []
            for pattern in track.findall("pattern"): # <-- Element (XML) type
                midi_pattern = Pattern(pos=int(pattern.attrib["pos"]), notes=[])
                for note in pattern:
                    note.attrib["len"] = 24 # Because for SOME REASON LMMS sets it to -192 (so this a quarter note now, see line 78 for the same number)
                    midi_pattern.add_note(Note(pos=int(note.attrib["pos"]), pan=int(note.attrib["pan"]), length=int(note.attrib["len"]), vol=float(note.attrib["vol"]) / 200, key=int(note.attrib["key"])))
                midi_patterns.append(midi_pattern)
            for pattern in midi_patterns: # <-- Pattern type
                for bbtco in all_bbtco:
                    pattern_length_measure = midi_song.get_measure_length() * ceil(pattern.get_length()/midi_song.get_measure_length())
                    for i in range(0, ceil(bbtco[1]/pattern_length_measure)):
                        clone = Pattern(pos=int(pattern.pos + bbtco[0] + i*pattern_length_measure), notes=[])
                        # Chops off patterns longer than the bbtco element
                        for note in pattern.clone_notes():
                            if (note.time + clone.pos) < (bbtco[0] + bbtco[1]): #"If the global start position of the note is less than/equal to than the global end position of the bbtco..."
                                clone.notes.append(note)
                        # Alright. We are FINALLY done with this hell.
                        midi_track.add_pattern(clone)
            # 7. Adds track
            midi_song.add_track(midi_track)
    return midi_song

def is_sf2_player(track):
    return track.find("instrumenttrack/instrument") and "name" in track.find("instrumenttrack/instrument").attrib and track.find("instrumenttrack/instrument").attrib["name"] == "sf2player"

def midi_track_from_xml(track):
    midi_track = Track(name=track.attrib["name"])
    midi_track.patch = int(track.find("instrumenttrack/instrument/sf2player").attrib["patch"])
    midi_track.bank = int(track.find("instrumenttrack/instrument/sf2player").attrib["bank"])
    midi_track.volume = float(track.find("instrumenttrack").attrib["vol"]) / 200
    midi_track.pan = float(track.find("instrumenttrack").attrib["pan"]) / 100
    return midi_track