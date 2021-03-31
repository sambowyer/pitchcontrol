import math

## MIDI-based helpers
def getMidiNoteWithCents(freq):
    return 69 + 12*math.log2(freq/440)

def getNoteName(freq):
    midiNote = round(getMidiNoteWithCents(freq))
    midiOctave = (midiNote // 12) - 1 
    return ("A","A#","B","C","C#","D","D#","E","F","F#","G","G#")[(midiNote+3) % 12] + str(midiOctave)

def getCents(freq):
    '''Returns the number of cents that *freq* is away from the nearest in-tune note. This means the int returned is between -49 and 50 (inclusive).'''
    remainder = getMidiNoteWithCents(freq) % 1
    if remainder <= 0.5:
        return round(remainder * 100)
    else:
        return round(remainder * 100) - 100

def midiToFreq(midiNote):
    return 440*(2**((midiNote - 69)/12))

def noteNameToMidi(noteName):
    octave = int(noteName[-1])
    noteNum = ("C","C#","D","D#","E","F","F#","G","G#","A","A#","B").index(noteName[:-1]) #start at C rather than A because octave numbers change at C, not A
    return 12+noteNum + 12*octave

def noteNameToFreq(noteName):
    return midiToFreq(noteNameToMidi(noteName))

def getPitchInfo(freq):
    cents = getCents(freq)
    if cents >= 0:
        return "%sHz - %s + %scents" % (freq, getNoteName(freq), cents)
    else:
        return "%sHz - %s - %scents" % (freq, getNoteName(freq), cents*-1)

def printPitchInfo(freq):
    print(getPitchInfo(freq))


## signal-based helpers
def toMono(signal):
    if type(signal[0] == list):
        return [sum(channels) for channels in signal]

def linearInterpolate(x1, x2, gamma):
    return (x1 + (x2-x1)*gamma)

def resample(signal, oldSampleRate, newSampleRate):
    resampledSignal = []
    for i in range(len(signal)):
        resampleIndex = i*oldSampleRate/newSampleRate
        if resampleIndex >= len(signal) - 1:
            break
        resampledSignal.append(linearInterpolate(signal[math.floor(resampleIndex)], signal[math.ceil(resampleIndex)], resampleIndex % 1))

    return resampledSignal


## stats helpers
def getTrimmedMean(data, trimSize):
    '''returns the mean of the list 'data' excluding its smallest and largest elements.
    The total proportion of the list to be excluded from the mean calculation is given by 'trimSize' - between 0 and 1.'''
    
    if trimSize > 1 or len(data) == 0:
        return None
    elif trimSize < 0:
        return sum(data)/len(data)
    sortedData = data.copy()
    sortedData.sort()
    trimIndices = [math.floor((len(data)-1)*trimSize), math.ceil((len(data)-1)*(1-trimSize))]
    trimIndices.sort()
    return sum(sortedData[trimIndices[0]:trimIndices[1]])/(trimIndices[1]-trimIndices[0])