import math
import numpy as np
import customFFT

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

def stretch(signal, desiredLength):
    '''Stretch out a signal to a new desired length (can be longer or shorter than the original signal) using linear interpolation. 
    Note that this will change the frequency of the signal.'''
    ratio = len(signal)/desiredLength
    interpolatedIndices = [i*ratio for i in range(desiredLength)]
    stretchedSignal = []
    for index in interpolatedIndices:
        stretchedSignal.append(linearInterpolate(signal[math.floor(index)], signal[math.ceil(index)], index % 1))

    return stretchedSignal

def clipSignal(signal, minMagnitude=-1, maxMagnitude=1):
    '''Clip a signal at values of *minMagnitude* and *maxMagnitude* - note that whilst these take default values -1 and 1 respectively, in order to conform with the values 
    given by the soundfile module as well as signalGenerator.py, they can be changed since different modules may have different standards e.g. sample values given as integers between 2147483648 and 2147483647.'''
    for i in range(len(signal)):
        signal[i] = max(signal[i], minMagnitude)
        signal[i] = min(signal[i], maxMagnitude)

    return signal

def multiplyGain(signal, scalar, clip=True, clipMin=-1, clipMax=1):
    for i in range(len(signal)):
        signal[i] *= scalar
    
    if clip:
        return clipSignal(signal,clipMin, clipMax)

    return signal
    
def multiplyGainUntilClipping(signal, clipMin=-1, clipMax=1):
    scalarToMinClip = clipMin/min(signal)
    scalarToMaxClip = clipMax/max(signal)
    return multiplyGain(signal, min(abs(scalarToMinClip), abs(scalarToMaxClip)), True, clipMin, clipMax)

def proportionClipping(signal, clipMin=-1, clipMax=1):
    clipCount = 0
    for i in signal:
        if i <= clipMin or i >= clipMax:
            clipCount += 1
    return clipCount / len(signal)

def addGaussianWhiteNoise(signal, std=0.05, clip=True, clipMin=-1, clipMax=1):
    for i in range(len(signal)):
        signal[i] += np.random.normal(0, std)

    if clip:
        return clipSignal(signal,clipMin, clipMax)

    return signal

# CONSIDER WHETHER TO KEEP THIS IN - window functions seem very interesting but it is a very big subject.
#   To include JUST a hanning window and no other types of window functions may seem pointless/rather arbitrary.
#   Plus it would likely require discussion in my report and I don't know whether I would be able to do it justice 
#   especially since it is just 'an aside' and not really one of the main parts of this project.
#   Though, perhaps it may be interesting to see if it does help with pitch detection - If it does (significantly) then 
#   it may be worth keeping it in and trying my best to justify just using Hanning windows and no other window functions
def getHanningWindow(length):
    return [(math.sin(math.pi*i/length))**2 for i in range(length)]

def fft(signal, isCustomFFT, fullLength=False):
    if isCustomFFT:
        return customFFT.fft(signal, fullLength)
    else:
        return np.fft.rfft(signal)

def ifft(signal, isCustomFFT, fullLength=False):
    if isCustomFFT:
        return customFFT.ifft(signal, fullLength)
    else:
        return np.fft.ifft(signal)

def STFT(signal, windowSize, overlap, isCustomFFT = False, windowFunction=None):
    if windowFunction == None:
        windowFunction = [1 for i in range(windowSize)]
    elif len(windowFunction) != windowSize:
        windowFunction = stretch(windowFunction, windowSize)

    N = len(signal)
    transforms = []
    startIndex = 0
    while startIndex + windowSize <= N:
        transforms.append(fft([signal[startIndex+i]*windowFunction[i] for i in range(windowSize)], isCustomFFT))
        startIndex += windowSize - overlap

    return transforms
    

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