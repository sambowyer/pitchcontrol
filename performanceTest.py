from testing import testToCSV
from helpers import *
import signalGenerator
import random
import soundfile as sf

# 19 important features to consider in total
# Since we are only testing one value (the optimal value) for each hyperparameter each signal will generate 9 lines in the csv file
#   i.e. 1 line for each of zerocross, autocorrelation, AMDF, naiveFT, naiveFTWithPhase, cepstrum, HPS, mean, median
csvData =  {"signalType" : "", "algorithm" : "", "b" : [0.5], "isCustomFFT" : [False], "numDownsamples" : [2], "octaveTrick" : [True], "sampleRate" : 44100,
            "expectedMin" : 20, "expectedMax" : 20000, "instrument" : "n/a", "noise" : 0,"extraGain" : 0, "windowFunction" : "rectangle", "trueFreq" : 0, "predFreq" : 0, "time" : 0, 
            "percentErr" : 0, "absMidiErr": 0, "correctNote" : 0, "correctNoteWithOctaveErr" : 0}


# Want to do tests all 250 instrument samples (saved as wav files) along with 250 generated signals
#       250 GENERATED SIGNALS breakdown: 
#           50 signals for each type from sine, saw, square, triangle, sineWithHarmonics (all at the optimal sample rate of 22050Hz (assuming we only want a fixed number of samples - 2048 - for efficiency)) 
#                  each with random frequency (and random number of harmonics in the case of sineWithHarmonics)
csvFile = "csvs/performanceTest.csv"
freqSRTypeCombinationsRecord = "testRecords/performanceTest-freqSRTypeCombinations.txt"
wavFilesRecord = "testRecords/performanceTest-wavFiles.txt"

#define the number of tests up here so that they can be easily changed - allowing us to stop and start testing as we want
generatedTestStartNum = 1
generatedTestEndNum = 250

wavTestStartNum = 251
wavTestEndNum = 500

## GENERATED SIGNALS
freqSRTypeCombinations = [""]
with open(freqSRTypeCombinationsRecord, "r") as f:
        freqSRTypeCombinations += [line.strip() for line in f.readlines()]

print("Already done: %s" % (freqSRTypeCombinations))

signalTypes = ["sine", "saw", "square", "triangle", "sineWithHarmonics"]
sampleRate = 22050
for testCount in range(generatedTestStartNum,generatedTestEndNum+1):
    freqSRType = ""
    signalType = signalTypes[int((testCount-1)//(generatedTestEndNum/5))]
    while freqSRType in freqSRTypeCombinations:
        freq = midiToFreq(33 + random.randrange(144)/2) #Pick a frequency between A1 and A7 (resolution is a quarter tone)
        if signalType == "sineWithHarmonics":
            numHarmonics = random.randrange(10,21)
            signalType += "(%s)" % (numHarmonics)
        freqSRType = "%s+%s+%s" % (freq, sampleRate, signalType)

    freqSRTypeCombinations.append(freqSRType)

    with open(freqSRTypeCombinationsRecord, "a") as f:
        f.write(freqSRType + "\n")
    
    #Give an expected frequency range of at least 3 octaves either side of the true frequency (whilst staying within the range of human hearing)
    expectedMin = max(20, freq/8)
    expectedMax = min(20000, freq*8) 

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
    csvData["expectedMin"] = expectedMin
    csvData["expectedMax"] = expectedMax
    csvData["trueFreq"] = freq

    testToCSV(signal, csvData, csvFile)

    print("%s/%s done. %s" % (testCount, wavTestEndNum, freqSRType))


## WAV SIGNALS
files = [""]
with open(wavFilesRecord, "r") as f:
        files += [line.strip() for line in f.readlines()]

print("Already done: %s" % (files))

instruments = ["piano","cello","violin","trumpet","flute"]
instrumentFolderNames = {"piano" : "LABSPiano",  "cello" : "BBCCello",  "violin" : "BBCViolin", "trumpet" : "BBCTrumpet", "flute" : "BBCFlute"}
instrumentRanges = {"piano" : [23.8,4836.32], "cello" : [56.51,1016.71], "violin" : [169.64,4066.84], "trumpet":[160.12,1357.15], "flute":[226.45,2418.16]}
instrumentSamplesAvailable = {"piano" : ["A0","C8"], "cello" : ["C2","A#5"], "violin" : ["G3","C#7"], "trumpet":["E3","D6"], "flute":["C4","C7"]}

testCount = wavTestStartNum
for instrument in instruments:
    noteName = instrumentSamplesAvailable[instrument][0]
    midiNote = noteNameToMidi(noteName)
    while midiNote <= noteNameToMidi(instrumentSamplesAvailable[instrument][1]):
        filePath = "wavs/instrumentSamples/%s/%s.wav" % (instrumentFolderNames[instrument], instrumentFolderNames[instrument] + noteName) 

        with open(wavFilesRecord, "a") as f:
            f.write(filePath + "\n")

        expectedMin = max(20, instrumentRanges[instrument][0])
        expectedMax =  min(20000, instrumentRanges[instrument][1])

        signalType = instrumentFolderNames[instrument] + noteName

        signal, sampleRate = sf.read(filePath)
        signal = toMono(signal)[2048:4096]

        csvData["signalType"] = signalType
        csvData["sampleRate"] = sampleRate
        csvData["expectedMin"] = expectedMin
        csvData["expectedMax"] = expectedMax
        csvData["trueFreq"] = midiToFreq(midiNote)
        csvData["instrument"] = instrument

        testToCSV(signal, csvData, csvFile)

        print("%s/%s done. %s" % (testCount, wavTestEndNum, filePath))

        files.append(filePath)
        midiNote += 1
        noteName = getNoteName(midiToFreq(midiNote))

        testCount += 1