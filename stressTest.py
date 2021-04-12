from testing import testToCSV
from helpers import *
import signalGenerator
import random
import soundfile as sf

# 19 important features to consider in total
# In this stress test we will be adding noise and increasing gain (so that the signals start clipping) on signals in order to see how the pitch detection algorithms
# compare when the signals are far from 'ideal'
# We will first normalise each signal (increasing the gain as much as possible before it starts to clip) and then run the pitch detection algorithms through variations of that signal
# These variations will be a combination of the following two procedures:
#       noise       - add gaussian white noise with a standard deviation amplitude of 0.005, 0.01, 0.05, 0.1]
#       extraGain   - multiply the signal by factors of 1.25, 1.5, 1.75, 2 (since the signal has already been normalised this will then result in (heavy) clipping)
# All possible combinations of these two procedures (with their different parameter values) will be tested
# 'Control' combinations will also be tested, i.e. where only one of the procedures is used and not the other
#       (Though we won't be testing any signals without EITHER procedure as those tests have already been done in optimisationTest.csv and performanceTest.csv)
# NOTE that in all cases we will first add the extra gain and THEN add noise (if both procedures are to be done) 
#       - multiplying AFTER adding noise would change the noise standard deviation (which would be calculable, but it makes more sense to consider the noise as 
#         being the last procedure since in practice noise is more likely to affect a signal on it's way to the pitch detection and not be an actual feature 
#         of that signal (whereas clipping could easily be a feature of the original signal))
# Hence, each signal will create *** lines in the csv:
#       'noise' has 5 possible parameter values (including the case where we don't add any noise)
#       'extraGain' has 5 possilbe parameter values (including the case where we don't add any extra gain)
#       So there are 24 (=5*5-1) signal variations to test per single original (unvaried) signal
#       Then there are 9 algorithms to test (including trimmedMean and median) so we get a total of 24*9 = 216
csvData =  {"signalType" : "", "algorithm" : "", "b" : [0.5], "isCustomFFT" : [False], "numDownsamples" : [2], "octaveTrick" : [True], "sampleRate" : 44100,
            "expectedMin" : 20, "expectedMax" : 20000, "instrument" : "n/a", "noise" : 0,"extraGain" : 0, "windowFunction" : "rectangle", "trueFreq" : 0, "predFreq" : 0, "time" : 0, 
            "percentErr" : 0, "absMidiErr": 0, "correctNote" : 0, "correctNoteWithOctaveErr" : 0}


# Want to do tests of all hyperparameter combinations with 100 signals total:
#       50 GENERATED SIGNALS 
#           (randomise frequency uniformly on MIDI scale (which is essentially a log(Hz) scale) with resolution of 0.5 and randomise sampleRate as either 22050Hz or 44100Hz)
#               (also for sineWithHarmonics, randomise the number of harmonics uniformly between 10 and 20 (inclusive))
#       50 WAV SIGNALS (INSTRUMENT SAMPLES) 
#           (randomise instrument and note)
# Since there is randomisation going on we want to keep track of these combinations so that we don't end up repeating signals as this would be a waste of computation time

csvFile = "csvs/stressTest.csv"
freqSRTypeCombinationsRecord = "testRecords/stressTest-freqSRTypeCombinations.txt"
wavFilesRecord = "testRecords/stressTest-wavFiles.txt"

#define the number of tests up here so that they can be easily changed - allowing us to stop and start testing as we want
generatedTestStartNum = 50
generatedTestEndNum = 50

wavTestStartNum = 91
wavTestEndNum = 100

# signal variation parameters to be used
extraGainValues = [1, 1.25, 1.5, 1.75, 2]
noiseSDValues = [0, 0.005,0.01,0.05,0.1]

## GENERATED SIGNALS
freqSRTypeCombinations = [""]
with open(freqSRTypeCombinationsRecord, "r") as f:
        freqSRTypeCombinations += [line.strip() for line in f.readlines()]

print("Already done: %s" % (freqSRTypeCombinations))

sampleRate = 44100
signalTypes = ["sine", "saw", "square", "triangle", "sineWithHarmonics"]

for testCount in range(generatedTestStartNum,generatedTestEndNum+1):
    freqSRType = ""
    while freqSRType in freqSRTypeCombinations:
        freq = midiToFreq(33 + random.randrange(144)/2) #Pick a frequency between A1 and A7 (resolution is a quarter tone)
        signalType = signalTypes[random.randrange(5)]
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

    #normalise the signal
    signal = multiplyGainUntilClipping(signal)

    csvData["signalType"] = signalType
    csvData["sampleRate"] = sampleRate
    csvData["expectedMin"] = expectedMin
    csvData["expectedMax"] = expectedMax
    csvData["trueFreq"] = freq

    variationCount = 1
    for extraGain in extraGainValues:
        for noiseSD in noiseSDValues:
            if noiseSD != 0 or extraGain != 1: #as long as both aren't their identity values - (thank you, De Morgan)
                signalVariation = addGaussianWhiteNoise(multiplyGain(signal, extraGain), noiseSD)

                csvData["noise"] = noiseSD
                csvData["extraGain"] = extraGain

                testToCSV(signalVariation, csvData, csvFile)

                print("    Variation %s/24 done. extraGain=%s, noiseSD=%s, proportionClipping=%s" % (variationCount, extraGain, noiseSD, proportionClipping(signalVariation)))
                variationCount += 1

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

    expectedMin = max(20, instrumentRanges[instrument][0])
    expectedMax = min(20000, instrumentRanges[instrument][1])

    signalType = instrumentFolderNames[instrument] + noteName

    signal, sampleRate = sf.read(filePath)
    signal = multiplyGainUntilClipping(toMono(signal)[2048:4096])

    csvData["signalType"] = signalType
    csvData["sampleRate"] = sampleRate
    csvData["expectedMin"] = expectedMin
    csvData["expectedMax"] = expectedMax
    csvData["trueFreq"] = midiToFreq(midiNote)
    csvData["instrument"] = instrument

    variationCount = 1
    for extraGain in extraGainValues:
        for noiseSD in noiseSDValues:
            if noiseSD != 0 or extraGain != 1: 
                signalVariation = addGaussianWhiteNoise(multiplyGain(signal, extraGain), noiseSD)
                
                csvData["noise"] = noiseSD
                csvData["extraGain"] = extraGain

                testToCSV(signalVariation, csvData, csvFile)

                print("    Variation %s/24 done. extraGain=%s, noiseSD=%s, proportionClipping=%s" % (variationCount, extraGain, noiseSD, proportionClipping(signalVariation)))
                variationCount += 1

    print("%s/%s done. %s" % (testCount, wavTestEndNum, filePath))