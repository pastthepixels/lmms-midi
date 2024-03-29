from array import ArrayType
from math import ceil, log2
from enum import Enum
from midiutil.MidiFile import MIDIFile
import xml.etree.ElementTree as ET
import copy as copy

# Constants
WIZARD_MODE = False

# NOTES --> PATTERNS --> REGULAR TRACKS

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
        self.length = -1
    
    def add_note(self, note:Note):
        self.notes.append(note)
    
    def to_string(self):
        string = "Pattern: "
        for idx, note in enumerate(self.notes):
            string += ("\n\t {0}. " + note.to_string()).format(idx)
        return string
    
    def get_length(self):
        calculated_length = self.notes[-1].time + self.notes[-1].duration
        if calculated_length > self.length or self.length == 1:
            return calculated_length
        else:
            return self.length
    
    def clone_notes(self):
        notes = []
        for note in self.notes:
            notes.append(note.clone())
        return notes

class Track:
    def __init__(self, name:str, bank:int=0, patch:int=0):
        self.automation_parameters = []
        self.patterns = []
        self.bank = bank
        self.patch = patch
        self.name = name
        self.volume = 0 # out of 1
        self.pan = 0 # -1 or 1
    
    def add_pattern(self, pattern:Pattern):
        self.patterns.append(pattern)

# AUTOMATION TRACKS

class AutomationTrackTypes(Enum):
     PITCH = 1
     VOLUME = 2
     PAN = 3

class AutomationParameter: # Put this in a Track
    def __init__(self, id:int, value:float, automation_type:int):
        # ID
        self.id = id
        # Value and automation type
        self.value = value
        self.automation_type = automation_type

    def to_string(self):
        return "AutomationParameter({0}): id={1}, value={2}".format(self.automation_type, self.id, self.value)

class AutomationKey:
    def __init__(self, time:int, value:float):
        self.time = time
        self.value = value

class AutomationPattern:
    def __init__(self, pos:int, ids:ArrayType, keys:ArrayType):
        self.keys = keys
        self.pos = pos
        self.ids = []

    def add_key(self, key:AutomationKey):
        self.keys.append(key)

class AutomationTrack:
    def __init__(self, patterns:ArrayType):
        self.patterns = patterns

    def add_pattern(self, pattern:AutomationPattern):
        self.patterns.append(pattern)

def find_automations_in_xml(track):
    automation_parameters = []
    for element in track.findall("instrumenttrack/*"):
        automation_type = None
        match element.tag:
            case "pitch":
                automation_type = AutomationTrackTypes.PITCH
            case "vol":
                automation_type = AutomationTrackTypes.VOLUME
            case "pan":
                automation_type = AutomationTrackTypes.PAN
            case _:
                continue # If it's not a part of the three main automation types it doesn't matter
        automation_parameters.append(AutomationParameter(int(element.attrib["id"]), float(element.attrib["value"]), automation_type))
    return automation_parameters

# Runs through all automation tracks in a song and gets all patterns that have a specific ID
def find_automation_patterns(song, id:int):
    automation_patterns = []
    for automation_track in song.automation_tracks:
        for automation_pattern in automation_track.patterns:
            if id in automation_pattern.ids:
                automation_patterns.append(automation_pattern)
    return automation_patterns

# value: float between -1 and 1
def apply_automation_key(automation_type:int, midi_file:MIDIFile, track_num:int, channel:int, time:int, value:float):
    match automation_type:
        case AutomationTrackTypes.PITCH:
            midi_file.addPitchWheelEvent(track_num, channel, time, int(value * 8192))

        case AutomationTrackTypes.VOLUME:
            midi_file.addControllerEvent(track_num, channel, time, 7, min(int(value * 255), 127))

        case AutomationTrackTypes.PAN:
            midi_file.addControllerEvent(track_num, channel, time, 10, min(int((value + 1) / 2 * 127), 127))

# SONGS

class Song:
    def __init__(self, filename:str="", bpm:int=120, timesig:ArrayType=[4, 4]):
        # Name/music information
        self.filename = filename
        self.bpm = bpm
        self.timesig = timesig
        # Tracks
        self.tracks = []
        # Automation
        self.automation_tracks = []
    
    def add_track(self, track:Track):
        self.tracks.append(track)

    def add_automation_track(self, automation_track:AutomationTrack):
        self.automation_tracks.append(automation_track)

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
                    note.pitch += 12 # TODO: FIX Have to raise everything by an octave for some reason. Very cool
                    midi_file.addNote(track_num, channel, note.pitch, (note.time + pattern.pos) / 48, note.duration / 48, int(note.volume * 127))
            
            for automation_parameter in track.automation_parameters:
                automation_patterns = find_automation_patterns(self, automation_parameter.id)
                for pattern in automation_patterns:
                    divisor = 100 # Sometimes volumes work on a different scale than pitches (and so on) so we can't always divide by 100 to get it to be normalized
                    match automation_parameter.automation_type:
                        case AutomationTrackTypes.PITCH:
                            divisor = 100

                        case AutomationTrackTypes.VOLUME:
                            divisor = 200

                        case AutomationTrackTypes.PAN:
                            divisor = 100

                    for idx, key in enumerate(pattern.keys):
                        apply_automation_key(automation_parameter.automation_type, midi_file, track_num, channel, (key.time + pattern.pos) / 48, key.value/divisor)
                        if (idx+1) < len(pattern.keys):
                            for i in range(0, pattern.keys[idx+1].time - key.time):
                                # TODO: Add support for different types of automation tracks which interpolate smoothly/not at all
                                value = (pattern.keys[idx+1].value - key.value) * i/(pattern.keys[idx+1].time - key.time) + key.value # Transitions linearly between two values by i%
                                apply_automation_key(automation_parameter.automation_type, midi_file, track_num, channel, (key.time + pattern.pos + i) / 48, value/divisor)

            if track.bank == 128: channel = oldchannel # Restores channel count as usual
            channel += 1

        with open(self.filename, 'wb') as outf:
            midi_file.writeFile(outf)
    
    def get_measure_length(self):
        return self.timesig[1] * 48

# LOADING FILES

def parse_xml(xml_path, output:str=None):
    # 1. Loads and parses XML
    tree = ET.parse(xml_path)
    root = tree.getroot()        
    # 2. Gets the <head> and <song> elements        
    head = root.find("head")
    song = root.find("song")
    # 3. Creates a Song instance with right name/bpm/time signature
    bpm = int(head.attrib["bpm"]) if "bpm" in head.attrib else int(head.find("bpm").attrib["value"])
    midi_song = Song(xml_path[:-4]+".mid" if output == None else output, bpm)
    midi_song.timesig = [int(head.attrib["timesig_numerator"]), int(head.attrib["timesig_denominator"])]
    # 4. Goes through each track, classifying them
    sf2_tracks = []
    sf2_bb_tracks = []
    automation_tracks = []
    for track in song.find("trackcontainer"):
        if is_sf2_player(track):
            sf2_tracks.append(track)
        if track.find("bbtrack") != None:
            sf2_bb_tracks.append(track)
        if track.find("automationtrack") != None:
            automation_tracks.append(track)
    # 5. Goes through each SF2 Player track
    for track in sf2_tracks:
        midi_song.add_track(midi_track_from_xml(track))
    # Easy, right? Well, just you wait until step 6...
    # 6. Goes through each SF2 Player Beat/Bassline trackfor automation_track in automation_tracks:
    if len(sf2_bb_tracks) > 0: add_bb_tracks(midi_song, sf2_bb_tracks)
    # 7. Goes through automation tracks
    for automation_track in automation_tracks:
        midi_atrack = AutomationTrack([])
        for automation_pattern in automation_track.findall("automationpattern"):
            midi_pattern = AutomationPattern(int(automation_pattern.attrib["pos"]), [], [])
            midi_pattern.keys = []
            for automation_object in automation_pattern.findall("object"):
                midi_pattern.ids.append(int(automation_object.attrib["id"]))
            for automation_key in automation_pattern.findall("time"):
                midi_pattern.add_key(AutomationKey(int(automation_key.attrib["pos"]), float(automation_key.attrib["value"])))
            midi_atrack.add_pattern(midi_pattern)
        midi_song.add_automation_track(midi_atrack)
    return midi_song

# Notes:
#   - The first Beat/Bassline track acts like a b/b track but ALSO like a header, defining each pattern.
#   - The first pattern in each sub-track corresponds to the first b/b track, and so on.
# I found out some of this through lynxwave.com/LMMStoMIDI; check it out!
def add_bb_tracks(midi_song:Song, sf2_bb_tracks:ArrayType):
    # Deal with the "header" beat/bassline track
    header_bb_track = sf2_bb_tracks[0]
    bb_tracks = [] # The *actual* tracks in beat/bassline tracks
    for track in header_bb_track.find("bbtrack/trackcontainer"):
        if is_sf2_player(track) == True: bb_tracks.append(midi_track_from_xml(track))
    # Deal with every beat/bassline track
    # Goes over each individual track:
    for track in bb_tracks:
        # Clones the track
        midi_track = copy.deepcopy(track)
        # Resets patterns in the clone
        midi_track.patterns = []
        # Goes over every beat/bassline track
        for (bb_track_idx, bb_track) in enumerate(sf2_bb_tracks):
            # Finds the right pattern to use (and fixes its time since the length of everything is -192 for some reason)
            pattern = track.patterns[bb_track_idx]
            pattern.pos = 0
            if len(pattern.notes) == 0: # Sometimes we actually get *empty* patterns. Yep!
                continue
            for note in pattern.notes:
                if note.duration <= 0: note.duration = 12 # 12 ticks, LMMS format. TECHNICALLY this is wrong as LMMS actually makes these notes as long as possible for some reason

            # Goes over each "repeat", called a bbtco for Beat/Bassline Track Container
            all_bbtco = []
            for child in bb_track:
                if child.tag == "bbtco" and child.attrib["muted"] == "0": all_bbtco.append([int(child.attrib["pos"]), int(child.attrib["len"])])

            # Trims/repeats the right pattern for the beat/bassline track
            for bbtco in all_bbtco:
                patterns_to_add = ceil(bbtco[1]/pattern.get_length()) # How much times we have to repeat a pattern to fit in the duration of a bbtco
                for i in range(0, patterns_to_add):
                    clone = copy.deepcopy(pattern)
                    clone.pos = int(bbtco[0]) + i*pattern.get_length()
                    clone.notes = []
                    # Chops off patterns longer than the bbtco element
                    for note in pattern.clone_notes():
                        if (note.time + clone.pos) < (bbtco[0] + bbtco[1]): #"If the global start position of the note is less than/equal to than the global end position of the bbtco..."
                            clone.notes.append(note)
                    # Alright. We are FINALLY done with this hell.
                    midi_track.add_pattern(clone)
        # Adds track
        midi_song.add_track(midi_track)

def is_sf2_player(track):
    condition = track.find("instrumenttrack/instrument") and "name" in track.find("instrumenttrack/instrument").attrib and track.find("instrumenttrack/instrument").attrib["name"] == "sf2player"
    if condition == False and WIZARD_MODE == True:
        condition = input("Track '{}' found to not be an SF2 player. Include it anyway? [y/N]: ".format(track.attrib["name"])).lower() == "y"
    return condition

def midi_track_from_xml(track):
    midi_track = Track(name=track.attrib["name"])
    try:
        # If the track is an SF2 player take the patch and bank from it
        midi_track.patch = int(track.find("instrumenttrack/instrument/sf2player").attrib["patch"])
        midi_track.bank = int(track.find("instrumenttrack/instrument/sf2player").attrib["bank"])
    except:
        # Otherwise set it to defaults
        if WIZARD_MODE == True:
            print("--- Failed to set patch and bank for track '{}'; Since you have wizard mode enabled you can choose what these are set to. ---".format(midi_track.name))
            print("If you don't know what to pick, just choose 0 for the default piano. You can also open LMMS with an SF2 player to look at what is available.")
            midi_track.patch = int(input("\t Patch: "))
            midi_track.bank = int(input("\t Bank: "))
        else:
            print("Failed to set patch and bank for track '{}'; setting both to 0. This could likely be due to it not being an SF2 player.".format(midi_track.name))
            midi_track.patch = 0
            midi_track.bank = 0
    midi_track.volume = float(track.find("instrumenttrack").attrib["vol"]) / 200 if "vol" in track.find("instrumenttrack").attrib else 1
    midi_track.pan = float(track.find("instrumenttrack").attrib["pan"]) / 100 if "pan" in track.find("instrumenttrack").attrib else 0
    midi_track.automation_parameters = find_automations_in_xml(track)

    # Loops through each pattern, adding notes
    for pattern in track.findall("pattern"):
        midi_pattern = Pattern(pos=int(pattern.attrib["pos"]), notes=[])
        for note in pattern:
            midi_pattern.add_note(Note(pos=int(note.attrib["pos"]), pan=int(note.attrib["pan"]), length=int(note.attrib["len"]), vol=float(note.attrib["vol"]) / 200, key=int(note.attrib["key"])))
        # Calculates the length of each pattern if it has the "steps" attribute
        if "steps" in pattern.attrib:
            midi_pattern.length = int(pattern.attrib["steps"]) * 12 # Remember: multiply steps by 12 ticks in LMMS time
        midi_track.add_pattern(midi_pattern)
    return midi_track

# Wizard mode-specific functions
def set_wizard_mode(bool):
    global WIZARD_MODE
    WIZARD_MODE = bool
