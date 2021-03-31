from midiutil import MIDIFile
from helpers import noteNameToMidi

class MIDINote:
    def __init__(self, noteNum, noteLength, volume=100):
        self.noteNum = noteNum
        self.noteLength = noteLength
        self.noteVolume = volume

def writeMIDI(midiNotes, writeLocation, tempo=60):
    track = 0
    channel = 0
    time = 0 #in beats

    midi = MIDIFile(1) #create empty MIDI object
    midi.addTempo(track, time, tempo)

    for note in midiNotes:
        if note.noteNum != None:
            midi.addNote(track, channel, note.noteNum, time, note.noteLength, note.noteLength)
        time += note.noteLength

    with open(writeLocation, "wb") as f:
        midi.writeFile(f)

def generateInstrumentChromatics():
    instrumentTessiturasByNoteName = {"LABSPiano" : ["A0","C8"],  "BBCcello" : ["C2","A#5"], "BBCviolin" : ["G3","C#7"], "BBCtrumpet":["E3","D6"], "BBCFlute":["C4","C7"]}

    instrumentChromatics = {}
    for instrument in instrumentTessiturasByNoteName:
        minMidiValue = noteNameToMidi(instrumentTessiturasByNoteName[instrument][0])
        maxMidiValue = noteNameToMidi(instrumentTessiturasByNoteName[instrument][1])

        instrumentChromatics[instrument] = [MIDINote(num, 2) for num in [val for pair in [(i, None) for i in range(minMidiValue, maxMidiValue+1)] for val in pair]]

        writeMIDI(instrumentChromatics[instrument], "MIDI/%sChromatic.mid" % (instrument))

generateInstrumentChromatics()