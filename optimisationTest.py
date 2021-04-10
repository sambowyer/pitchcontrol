from testing import testToCSV
from helpers import *
import signalGenerator
import random
import soundfile as sf

# 19 important features to consider in total
# Note that the algorithm hyperparameters have values given by lists - testToCSV will try out all of the possible combinations of these.(*)
#       (*) (EXCEPT for mean/median which won't consider different combinations of isCustomFFT - they will assume that this values stays the same between all  
#            time-domain algorithms since it won't impact on the predicted frequency and is instead mainly useful to consider as far as computation times are concerned)
#
#   So in this particular instance, for 1 signal we will be generating a total of 95 lines in the csv file:
#       1 from zerocross
#       1 from autocorrelation
#       3 from AMDF     (since b can take 3 values)
#       2 from naiveFT  (since isCustomFFT can take 2 values)
#       2 from naiveFTWithPhase (since isCustomFFT can take 2 values)
#       2 from cepstrum (since isCustomFFT can take 2 values)
#       12 from HPS     (since isCustomFFT can take 2 values, numDownsamples can take 3 and octaveTrick can take 2. We then have 2x3x2 = 12)
#       36 from mean    (since each of the 12 HPS lines (each corresponding to just one other combination of hyperparameters other than b - see (*)) can be combined with any of the 3 lines from AMDF)
#       36 from median  (the same as for mean)
csvData =  {"signalType" : "", "algorithm" : "", "b" : [0.5,1,2], "isCustomFFT" : [False, True], "numDownsamples" : [2,4,6], "octaveTrick" : [False,True], "sampleRate" : 44100,
            "expectedRange" : [20,20000], "instrument" : "n/a", "noise" : 0,"extraGain" : 0, "windowFunction" : "rectangle", "trueFreq" : 0, "predFreq" : 0, "time" : 0, 
            "percentErr" : 0, "absMidiErr": 0, "correctNote" : 0, "correctNoteWithOctaveErr" : 0}


# Want to do tests of all hyperparameter combinations with 100 signals total:
#       50 GENERATED SIGNALS 
#           (randomise frequency uniformly on MIDI scale (which is essentially a log(Hz) scale) with resolution of 0.5 and randomise sampleRate as either 22050Hz or 44100Hz)
#               (also for sineWithHarmonics, randomise the number of harmonics uniformly between 10 and 20 (inclusive))
#       50 WAV SIGNALS (INSTRUMENT SAMPLES) 
#           (randomise instrument and note)
# Since there is randomisation going on we want to keep track of these combinations so that we don't end up repeating signals as this would be a waste of computation time

csvFile = "csvs/optimisationTest.csv"
freqSRTypeCombinationsRecord = "testRecords/optimisationTest-freqSRTypeCombinations.txt"
wavFilesRecord = "testRecords/optimisationTest-wavFiles.txt"

#define the number of tests up here so that they can be easily changed - allowing us to stop and start testing as we want
generatedTestStartNum = 1
generatedTestEndNum = 2

wavTestStartNum = 3
wavTestEndNum = 4

## GENERATED SIGNALS
freqSRTypeCombinations = [""]
with open(freqSRTypeCombinationsRecord, "r") as f:
        freqSRTypeCombinations += [line.strip() for line in f.readlines()]

print("Already done: %s" % (freqSRTypeCombinations))

sampleRates = [44100, 22050]
signalTypes = ["sine", "saw", "square", "triangle", "sineWithHarmonics"]

for testCount in range(generatedTestStartNum,generatedTestEndNum+1):
    freqSRType = ""
    while freqSRType in freqSRTypeCombinations:
        freq = midiToFreq(33 + random.randrange(144)/2) #Pick a frequency between A1 and A7 (resolution is a quarter tone)
        sampleRate = sampleRates[random.randrange(2)]
        signalType = signalTypes[random.randrange(5)]
        if signalType == "sineWithHarmonics":
            numHarmonics = random.randrange(10,21)
            signalType += "(%s)" % (numHarmonics)
        freqSRType = "%s+%s+%s" % (freq, sampleRate, signalType)

    freqSRTypeCombinations.append(freqSRType)

    with open(freqSRTypeCombinationsRecord, "a") as f:
        f.write(freqSRType + "\n")

    expectedRange = [max(20, freq/8), min(20000, freq*8)] #Give an expected frequency range of at least 3 octaves either side of the true frequency (whilst staying within the range of human hearing)

    if signalType == "sine":
        signal = signalGenerator.getSine(freq, 2048, sampleRate)
    elif signalType == "saw":
        signal = signalGenerator.getSaw(freq, 2048, sampleRate)
    elif signalType == "square":
        signal = signalGenerator.getSquare(freq, 2048, sampleRate)
    elif signalType == "triangle":
        signal = signalGenerator.getTriangle(freq, 2048, sampleRate)
    else:
        signal = signalGenerator.getSineWithHarmonics(freq, 2048, sampleRate, numHarmonics)

    csvData["signalType"] = signalType
    csvData["sampleRate"] = sampleRate
    csvData["expectedRange"] = expectedRange
    csvData["trueFreq"] = freq

    testToCSV(signal, csvData, csvFile)

    print("%s/100 done. %s" % (testCount, freqSRType))


## WAV SIGNALS
files = [""]
with open(wavFilesRecord, "r") as f:
        files += [line.strip() for line in f.readlines()]

print("Already done: %s" % (files))

instruments = ["piano","cello","violin","trumpet","flute"]
instrumentFolderNames = {"piano" : "LABSPiano",  "cello" : "BBCCello",  "violin" : "BBCViolin", "trumpet" : "BBCTrumpet", "flute" : "BBCFlute"}
instrumentRanges = {"piano" : [23.8,4836.32], "cello" : [56.51,1016.71], "violin" : [169.64,4066.84], "trumpet":[160.12,1357.15], "flute":[226.45,2418.16]}
instrumentSamplesAvailable = {"piano" : ["A0","C8"], "cello" : ["C2","A#5"], "violin" : ["G3","C#7"], "trumpet":["E3","D6"], "flute":["C4","C7"]}

for testCount in range(wavTestStartNum,wavTestEndNum+1):
    filePath = ""
    while filePath in files:
        instrument = instruments[random.randrange(5)]
        midiNote = random.randrange(noteNameToMidi(instrumentSamplesAvailable[instrument][0]), noteNameToMidi(instrumentSamplesAvailable[instrument][1])+1)
        noteName = getNoteName(midiToFreq(midiNote))
        filePath = "wavs/instrumentSamples/%s/%s.wav" % (instrumentFolderNames[instrument], instrumentFolderNames[instrument] + noteName) 

    files.append(filePath)

    with open(wavFilesRecord, "a") as f:
        f.write(filePath + "\n")

    expectedRange = [max(20, instrumentRanges[instrument][0]), min(20000, instrumentRanges[instrument][1])]

    signalType = instrumentFolderNames[instrument] + noteName

    signal, sampleRate = sf.read(filePath)
    signal = toMono(signal)[2048:4096]

    csvData["signalType"] = signalType
    csvData["sampleRate"] = sampleRate
    csvData["expectedRange"] = expectedRange
    csvData["trueFreq"] = midiToFreq(midiNote)
    csvData["instrument"] = instrument

    testToCSV(signal, csvData, csvFile)

    print("%s/100 done. %s" % (testCount, filePath))