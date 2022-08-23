import xml.etree.ElementTree as ET
from midiutil.MidiFile import MIDIFile

class Song:
    name = ""
    bpm = 0
    tracks = []
    def __init__(self, name, bpm = 120):
        self.name = name
        self.bpm = bpm
    
    def add_track(self, track):
        self.tracks.append(track)

    def compile_export(self):
        midi_file = MIDIFile(len(self.tracks))
        channel = 0
        for track_num, track in enumerate(self.tracks):
            if channel == 9: channel += 1 # Skips ahead if on channel 9 without being set there
            oldchannel = channel
            if track.bank == 128: channel = 9 # Sets to channel 9 (drums) if bank is set to the one where there's drums
           
            midi_file.addTrackName(track_num, 0, track.name)
            midi_file.addTempo(track_num, channel, self.bpm)
            midi_file.addProgramChange(track_num, channel, 0, track.patch) # Channel num (2nd variable) == track num

            for pattern in track.patterns:
                for note in pattern.notes:
                    note.pitch += 12 # Have to raise everything by an octave for some reason. Very cool
                    midi_file.addNote(track_num, channel, note.pitch, (note.time + pattern.pos) / 48, note.duration / 48, int((note.volume/200 * track.volume/200) * 255))
            
            if track.bank == 128: channel = oldchannel # Restores channel count as usual
            channel += 1

        with open("{0}.mid".format(self.name), 'wb') as outf:
            midi_file.writeFile(outf)

class Track:
    name = ""
    bank = 0
    patch = 0
    volume = 0 # out of 200
    patterns = []
    def __init__(self, name, bank = 0, patch = 0):
        self.patterns = []
        self.bank = bank
        self.patch = patch
        self.name = name
    
    def add_pattern(self, pattern):
        self.patterns.append(pattern)

class Note:
    pitch = 0
    pan = 0
    time = 0
    duration = 0
    volume = 0 # out of 200

    def __init__(self, pos = 0, pan = 0, length = 1, vol = 100, key = 60):
        self.pitch = key
        self.time = pos
        self.duration = length
        self.volume = vol
        self.pan = pan
    
    def to_string(self):
        return "Note: pitch={0}, time={1}, duration={2}, volume={3}, pan{4}".format(self.pitch, self.time, self.duration, self.volume, self.pan)

class Pattern:
    notes = []
    pos = 0
    def __init__(self, pos, notes):
        self.pos = pos
        self.notes = notes
    
    def add_note(self, note):
        self.notes.append(note)
    
    def to_string(self):
        string = "Pattern: "
        for idx, note in enumerate(self.notes):
            string += ("\n\t {0}. " + note.to_string()).format(idx)
        return string

def parse_xml(xml_path):
    # 1. Loads and parses XML
    tree = ET.parse(xml_path)
    root = tree.getroot()        
    # 2. Gets the <head> and <song> elements        
    head = root[0]
    song = root[1]
    # 3. Creates a Song instance with right name/bpm/time signature
    midi_song = Song(xml_path, int(head.attrib["bpm"]))
    # 4. Goes through each track, ensuring it's a SF2 Player
    sf2_tracks = []
    for child in song[0]:
        if "name" in child[0][0].attrib and child[0][0].attrib["name"] == "sf2player": sf2_tracks.append(child)
    # 5. Goes through each SF2 Player track
    for track in sf2_tracks:
        midi_track = Track(name=track.attrib["name"])
        midi_track.patch = int(track[0][0][0].attrib["patch"])
        midi_track.bank = int(track[0][0][0].attrib["bank"])
        midi_track.volume = float(track[0].attrib["vol"])
        # 6. Checks for patterns
        patterns = []
        for child in track:
            if child.tag == "pattern": patterns.append(child)
        # 7. Loops through each bar, adding notes
        for pattern in patterns:
            midi_pattern = Pattern(pos=int(pattern.attrib["pos"]), notes=[])
            for note in pattern:
                midi_pattern.add_note(Note(pos=int(note.attrib["pos"]), pan=int(note.attrib["pan"]), length=int(note.attrib["len"]), vol=int(note.attrib["vol"]), key=int(note.attrib["key"])))
            midi_track.add_pattern(midi_pattern)
        # 8. Adds track
        midi_song.add_track(midi_track)
    return midi_song