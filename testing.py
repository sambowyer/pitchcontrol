from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS
import signalGenerator
from PitchProfile import PitchProfile
from helpers import *
import soundfile as sf
from timeit import default_timer as timer
import os.path

def testAllAlgorithmsToCSV(signal, sampleRate, signalType, trueFreq, csvFilePath):
    '''If the document csvFilePath already exists, this function assumes that the file already contains headers: signalName, sampleRate, algorithm, algorithmParameters, trueFreq, predFreq, time
    Else, it creates the file csvFilePath and writes those headers as the first line.
    In either case, the function then writes in the relevant data generated by predicting the pitch of 'signal' using all prediction algorithms.'''

    fileAlreadyExists = False
    if os.path.isfile(csvFilePath):
        fileAlreadyExists = True

    with open(csvFilePath, "a") as f:
        if not fileAlreadyExists:
            f.write("signalType,sampleRate,algorithm,algorithmParameters,trueFreq,predFreq,time\n")
        
        ##  execute predictions in the following order: 
        ##      zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS (then all of those averaged out (excluding min and max estimates))

        executionTimes = []
        predictions = []

        #params may be changed later to get a wider range of results
        params = {"b" : 1, "isCustomFFT" : False, "numDownsamples" : 4}

        ## Calculations

        #zerocross
        start = timer()
        pred = predict.zerocross(signal, sampleRate)
        end = timer()

        predictions.append(pred)
        executionTimes.append(end-start)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "zerocross", "n/a", trueFreq, pred, end-start))

        #autocorrelation
        start = timer()
        pred = predict.autocorrelation(signal, sampleRate)
        end = timer()

        predictions.append(pred)
        executionTimes.append(end-start)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "autocorrelation", "n/a", trueFreq, pred, end-start))


        #AMDF
        start = timer()
        pred = predict.AMDF(signal, sampleRate, params["b"])
        end = timer()

        predictions.append(pred)
        executionTimes.append(end-start)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "AMDF", "b=" + str(params["b"]), trueFreq, pred, end-start))

        #naiveFT
        start = timer()
        pred = predict.naiveFT(signal, sampleRate, params["isCustomFFT"])
        end = timer()

        predictions.append(pred)
        executionTimes.append(end-start)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "naiveFT", "isCustomFFT=" + str(params["isCustomFFT"]), trueFreq, pred, end-start))

        #cepstrum
        start = timer()
        pred = predict.cepstrum(signal, sampleRate, params["isCustomFFT"])
        end = timer()

        predictions.append(pred)
        executionTimes.append(end-start)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "cepstrum", "isCustomFFT=" + str(params["isCustomFFT"]), trueFreq, pred, end-start))

        #HPS
        start = timer()
        pred = predict.HPS(signal, sampleRate, params["isCustomFFT"], params["numDownsamples"])
        end = timer()

        predictions.append(pred)
        executionTimes.append(end-start)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "HPS", "isCustomFFT=" + str(params["isCustomFFT"]) + "&numDownsamples=" + str(params["numDownsamples"]), trueFreq, pred, end-start))

        #average - exclude min and max
        pred = predict.getTrimmedMean(predictions, 1/3)
        time = sum(executionTimes)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "average", "b=" + str(params["b"]) + "&isCustomFFT=" + str(params["isCustomFFT"]) + "&numDownsamples=" + str(params["numDownsamples"]), trueFreq, pred, time))

        #median (exclude 1st and 2nd mins/maxs)
        pred = predict.getTrimmedMean(predictions, 2/3)
        time = sum(executionTimes)

        f.write("%s,%s,%s,%s,%s,%s,%s\n" % (signalType, sampleRate, "median", "b=" + str(params["b"]) + "&isCustomFFT=" + str(params["isCustomFFT"]) + "&numDownsamples=" + str(params["numDownsamples"]), trueFreq, pred, time))

def expectedIntervalTest():

    #autocorrelation
    print("autocorrelation")

    #octave error
    print("ACTUAL: 1500Hz OLD: 747Hz NEW: ", end="")
    printPitchInfo(autocorrelation(signalGenerator.getSaw(1500,2048,44100), 44100, expectedMin=1000, expectedMax=3000)) # -> 747
    print("^expectedMin=1000, expectedMax=3000")
    print("ACTUAL: 1500Hz OLD: 747Hz NEW: ", end="")
    printPitchInfo(autocorrelation(signalGenerator.getSquare(1500,2048,44100), 44100, expectedMin=1000, expectedMax=3000)) # -> 747
    print("^expectedMin=1000, expectedMax=3000")

    #other error
    print("ACTUAL: 2500Hz OLD: 832Hz NEW: ", end="")
    printPitchInfo(autocorrelation(signalGenerator.getTriangle(2500,2048,44100), 44100, expectedMin=1500, expectedMax=4000)) # -> 832
    print("^expectedMin=1500, expectedMax=4000")
    print("ACTUAL: 5000Hz OLD: 454Hz NEW: ", end="")
    printPitchInfo(autocorrelation(signalGenerator.getSaw(5000,2048,44100), 44100, expectedMin=3000, expectedMax=9000)) # -> 454
    print("^expectedMin=3000, expectedMax=9000")

    ####


    #AMDF
    print("\nAMDF")

    #octave error
    print("ACTUAL: 600Hz OLD: 300Hz NEW: ", end="")
    printPitchInfo(AMDF(signalGenerator.getSaw(600,2048,44100), 44100, expectedMin=330, expectedMax=1500)) # -> 300
    print("^expectedMin=330, expectedMax=1500")
    print("ACTUAL: 600Hz OLD: 300Hz NEW: ", end="")
    printPitchInfo(AMDF(signalGenerator.getSquare(600,2048,44100), 44100, expectedMin=330, expectedMax=1500)) # -> 300
    print("^expectedMin=330, expectedMax=1500")

    #other error
    print("ACTUAL: 500 Hz OLD: 100Hz NEW: ", end="")
    printPitchInfo(AMDF(signalGenerator.getTriangle(500,2048,44100), 44100, expectedMin=300, expectedMax=1000)) # -> 100
    print("^expectedMin=300, expectedMax=1000")
    print("ACTUAL: 600Hz OLD: 150Hz NEW: ", end="")
    printPitchInfo(AMDF(signalGenerator.getSine(600,2048,44100), 44100, expectedMin=250, expectedMax=1500)) # -> 150
    print("^expectedMin=250, expectedMax=1500")

    ####


    #naiveFT
    print("\nnaiveFT")

    #octave error 
    print("ACTUAL: 1500Hz OLD: 7052Hz NEW: ", end="")
    printPitchInfo(naiveFT(signalGenerator.getSaw(1500,2048,22050), 22050, False, expectedMin=800, expectedMax=3000)) # -> 7052
    print("^expectedMin=800, expectedMax=3000")
    print("ACTUAL: 1500Hz OLD: 7052Hz NEW: ", end="")
    printPitchInfo(naiveFT(signalGenerator.getSquare(1500,2048,22050), 22050, False, expectedMin=800, expectedMax=3000)) # -> 7052
    print("^expectedMin=800, expectedMax=3000")

    #other error
    print("ACTUAL: 12500Hz OLD: 9549Hz NEW: ", end="")
    printPitchInfo(naiveFT(signalGenerator.getSine(12500,2048,22050), 22050, False, expectedMin=10000, expectedMax=15000)) # -> 9549
    print("^expectedMin=10000, expectedMax=15000")
    print("ACTUAL: 17500Hz OLD: 4554Hz NEW: ", end="")
    printPitchInfo(naiveFT(signalGenerator.getTriangle(17500,2048,22050), 22050, False, expectedMin=10000)) # -> 4554
    print("^expectedMin=10000")

    # ####


    #cepstrum
    print("\ncepstrum")

    #other error
    print("ACTUAL: 300Hz OLD: 3678Hz NEW: ", end="")
    printPitchInfo(cepstrum(signalGenerator.getTriangle(300,2048,44100), 44100, False, expectedMax=1500)) # -> 3678
    print("^expectedMax=1500")
    print("ACTUAL: 300Hz OLD: 3678Hz NEW: ", end="")
    printPitchInfo(cepstrum(signalGenerator.getSineWithHarmonics(300,2048,44100, 20), 44100, False, expectedMax=1500)) # -> 3678
    print("^expectedMax=1500")
    print("ACTUAL: 900Hz OLD: 269Hz NEW: ", end="")
    printPitchInfo(cepstrum(signalGenerator.getSquare(900,2048,44100), 44100, False, expectedMin=300, expectedMax=1500)) # -> 269
    print("^expectedMin=300, expectedMax=1500")

    ####


    #HPS
    print("\nHPS")

    #octave error
    print("ACTUAL: 12500Hz OLD: 6589Hz NEW: ", end="")
    printPitchInfo(HPS(signalGenerator.getTriangle(12500,2048,44100), 44100, False, 4, expectedMin=7500, expectedMax=16000)) # -> 6589
    print("^expectedMin=7500, expectedMax=16000")
    print("ACTUAL: 12500Hz OLD: 6589Hz NEW: ", end="")
    printPitchInfo(HPS(signalGenerator.getSquare(12500,2048,44100), 44100, False, 4, expectedMin=7500, expectedMax=16000)) # -> 6589
    print("^expectedMin=7500, expectedMax=16000")

    #other error
    print("ACTUAL: 400Hz OLD: 129Hz NEW: ", end="")
    printPitchInfo(HPS(signalGenerator.getTriangle(400,2048,44100), 44100, False, 4, expectedMin=200, expectedMax=1500)) # -> 129
    print("^expectedMin=200, expectedMax=1500")
    print("ACTUAL: 400Hz OLD: 129Hz NEW: ", end="")
    printPitchInfo(HPS(signalGenerator.getSine(400,2048,44100), 44100, False, 4, expectedMin=200, expectedMax=1500)) # -> 129
    print("^expectedMin=200, expectedMax=1500")
    print("ACTUAL: 1500Hz OLD: 4500Hz NEW: ", end="")
    printPitchInfo(HPS(signalGenerator.getSaw(1500,2048,44100), 44100, False, 4, expectedMin=800, expectedMax=3000)) # -> 4500
    print("^expectedMin=800, expectedMax=3000")
    print("ACTUAL: 1500Hz OLD: 4500Hz NEW: ", end="")
    printPitchInfo(HPS(signalGenerator.getSquare(1500,2048,44100), 44100, False, 4, expectedMin=800, expectedMax=3000)) # -> 4500
    print("^expectedMin=800, expectedMax=3000")

def generatedSignalsTest(freqs = [50,100,200,300,400,440,500,800,1000,2000,4000,8000,10000,15000]):
    for freq in freqs:
        sine = signalGenerator.getSine(freq, 1024, 44100)
        square = signalGenerator.getSquare(freq, 1024, 44100)
        saw = signalGenerator.getSaw(freq, 1024, 44100)
        triangle = signalGenerator.getTriangle(freq, 1024, 44100)
        sineHarmonics = signalGenerator.getSineWithHarmonics(freq, 1024, 44100, 15)

    ########
        start = timer()
        pred = zerocross(sine, 44100)
        end = timer()
        print("Sine     %sHz: %sHz (zerocross)       - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = autocorrelation(sine, 44100)
        end = timer()
        print("Sine     %sHz: %sHz (autocorrelation) - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = cepstrum(sine, 44100, False)
        end = timer()
        print("Sine     %sHz: %sHz (cepstrum)       - took %ss" % (freq, pred, end-start))

    ########
        start = timer()
        pred = zerocross(square, 44100)
        end = timer()
        print("Sqaure   %sHz: %sHz (zerocross)       - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = autocorrelation(square, 44100)
        end = timer()
        print("Square   %sHz: %sHz (autocorrelation) - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = cepstrum(square, 44100, False)
        end = timer()
        print("Square   %sHz: %sHz (cepstrum) - took %ss" % (freq, pred, end-start))

    ########
        start = timer()
        pred = zerocross(saw, 44100)
        end = timer()
        print("Sawtooth %sHz: %sHz (zerocross)       - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = autocorrelation(saw, 44100)
        end = timer()
        print("Sawtooth %sHz: %sHz (autocorrelation) - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = cepstrum(saw, 44100, False)
        end = timer()
        print("Sawtooth %sHz: %sHz (cepstrum) - took %ss" % (freq, pred, end-start))

    ########

        start = timer()
        pred = zerocross(triangle, 44100)
        end = timer()
        print("Triangle %sHz: %sHz (zerocross)       - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = autocorrelation(triangle, 44100)
        end = timer()
        print("Triangle %sHz: %sHz (autocorrelation) - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = cepstrum(triangle, 44100, False)
        end = timer()
        print("Triangle %sHz: %sHz (cepstrum) - took %ss" % (freq, pred, end-start))

    ########

        start = timer()
        pred = zerocross(sineHarmonics, 44100)
        end = timer()
        print("sineHarmonics %sHz: %sHz (zerocross)       - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = autocorrelation(sineHarmonics, 44100)
        end = timer()
        print("sineHarmonics %sHz: %sHz (autocorrelation) - took %ss" % (freq, pred, end-start))

        start = timer()
        pred = cepstrum(sineHarmonics, 44100, False)
        end = timer()
        print("sineHarmonics %sHz: %sHz (cepstrum) - took %ss" % (freq, pred, end-start))

def midiTest():
    notesToTest = ["A0", "B0", "C1", "G1","D2","F#2","C#3","G#4","A4","E5","A#6","D#7","F7","B7","C8"]
    freqsToTest = [25,50,78,110,169,200,220,350,430,439,440,441,600,900,1250,1700,2500,4000,7500,12500,16000,18000,20000]

    for note in notesToTest:
        print("NOTE: %s FREQ: %s MIDI: %s" % (note, noteNameToMidi(note), midiToFreq(noteNameToMidi(note))))

    print()

    for freq in freqsToTest:
        printPitchInfo(freq)

def generateInstrumentFrequencyRanges():
    instrumentRanges = {"piano" : ["A0","C8"], "guitar" : ["E2","E6"], "cello" : ["C2","A5"], "violin" : ["G3","A7"],
                        "voice" : ["F2","A5"], "bass guitar" : ["E1","E5"], "trumpet" : ["F#3","D6"]}
    freqRanges = {}
    freqRangesPlus250Cents = {}
    for instrument in instrumentRanges:
        freqRanges[instrument] = [noteNameToFreq(instrumentRanges[instrument][0]), noteNameToFreq(instrumentRanges[instrument][1])]
        freqRangesPlus250Cents[instrument] = [midiToFreq(noteNameToMidi(instrumentRanges[instrument][0])-2.5), midiToFreq(noteNameToMidi(instrumentRanges[instrument][1])+2.5)]

    for instrument in instrumentRanges:
        print("%s - RANGE=%s RANGE+25s0cents=%s" % (instrument, freqRanges[instrument], freqRangesPlus250Cents[instrument]))

def pitchProfileTest1():
    filename = "uhhh-gentle-female-singing_B_major.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp = PitchProfile("wavs/" + filename, sampleRate, "naiveFT", {"isCustomFFT" : False}, "voice", 2048, "female-ooh")
    pp.writeLog("logs/" + pp.name + "EMPTY.log")
    pp.analysePitch()
    pp.printLog()
    pp.writeLog("logs/" + pp.name + ".log")

    filename = "choir-boy-solo-singing_150bpm_D_minor.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp = PitchProfile("wavs/" + filename, sampleRate, "naiveFT", {"isCustomFFT" : False}, "voice", 2048, "choirboy")
    pp.writeLog("logs/" + pp.name + "EMPTY.log")
    pp.analysePitch()
    pp.printLog()
    pp.writeLog("logs/" + pp.name + ".log")

    filename = "wee-spoken-vocal-fx_140bpm_C_minor.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp = PitchProfile("wavs/" + filename, sampleRate, "HPS", {"isCustomFFT" : False, "numDownsamples" : 4}, "voice", 1024)
    pp.analysePitch()
    pp.printLog()
    pp.writeLog("logs/" + pp.name + ".log")

pitchProfileTest1()

# printPitchInfo(440)

# data, samplerate = sf.read('wavs/guitarC3.wav')
# print(zerocross(toMono(data[1000:3048]), samplerate))
# print(autocorrelation(toMono(data[1000:3048]), samplerate))

# printPitchInfo(cepstrum(toMono(data[1000:5096]), samplerate))
# printPitchInfo(cepstrum(signalGenerator.getSineWithHarmonics(440,2048,22050, 20), 44100))

# print(AMDF(toMono(data[1000:3048]), samplerate))
# print(AMDF(signalGenerator.getSineWithHarmonics(440,1024,44100,20),44100,0.5))
# print(AMDF(signalGenerator.getSine(440,1024,44100),44100,1))

# data, samplerate = sf.read('440sine.wav') #data is of type float_64 by default
# print(sf.info('440sine.wav', verbose=True))

# print(zerocross(data, 44100))
# print(autocorrelation(data, 44100))

# printPitchInfo(zerocross(signalGenerator.getSaw(100,2048,44100), 44100))
# printPitchInfo(autocorrelation(signalGenerator.getSaw(100,2048,44100), 44100))
# printPitchInfo(AMDF(signalGenerator.getSaw(100,2048,44100), 44100))
# printPitchInfo(naiveFT(signalGenerator.getSaw(100,2048,44100), 44100, False))
# printPitchInfo(cepstrum(signalGenerator.getSaw(100,2048,44100), 44100, False))
# printPitchInfo(HPS(signalGenerator.getSaw(100,2048,44100), 44100, False, 4))

