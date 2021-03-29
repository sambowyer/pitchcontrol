import math

## MIDI-based helpers
def getMidiNoteWithCents(freq):
    return 69 + 12*math.log2(freq/440)

def getNoteName(freq):
    midiNote = round(getMidiNoteWithCents(freq))
    midiOctave = (midiNote // 12) - 1 
    return ("A","A#","B","C", "C#","D", "D#","E","F", "F#","G", "G#")[(midiNote+3) % 12] + str(midiOctave)

def getCents(freq):
    return round(getMidiNoteWithCents(freq) % 1 * 100)

def printPitchInfo(freq):
    print("%sHz - %s + %scents" % (freq, getNoteName(freq), getCents(freq)))


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
    if trimSize > 1:
        return sum
    sortedData = data.copy()
    sortedData.sort()
    trimIndices = [math.floor((len(data)-1)*trimSize), math.ceil((len(data)-1)*(1-trimSize))]
    trimIndices.sort()
    return sum(sortedData[trimIndices[0]:trimIndices[1]])/(trimIndices[1]-trimIndices[0])