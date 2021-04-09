from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS, naiveFTWithPhase
import signalGenerator
from PitchProfile import PitchProfile
from pitchShift import phaseVocoderPitchShift, phaseVocoderStretch, matchPitch
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
                        "voice" : ["F2","A5"], "bass guitar" : ["E1","E5"], "trumpet" : ["F#3","D6"], "flute" : ["C4","C7"]}
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

def octaveTrickTest1():
    print("CASES TO BE FIXED")
    print("HPS - Saw 1000Hz")
    print("Without octave trick: " + getPitchInfo(HPS(signalGenerator.getSaw(1000,2048,44100), 44100, False, 4, octaveTrick=False)))
    print("With octave trick:    " + getPitchInfo(HPS(signalGenerator.getSaw(1000,2048,44100), 44100, False, 4, octaveTrick=True)))
    print()

    print("HPS - SineWith10Harmonics 700Hz")
    print("Without octave trick: " + getPitchInfo(HPS(signalGenerator.getSineWithHarmonics(700,2048,44100,10), 44100, False, 4, octaveTrick=False)))
    print("With octave trick:    " + getPitchInfo(HPS(signalGenerator.getSineWithHarmonics(700,2048,44100,10), 44100, False, 4, octaveTrick=True)))
    print()

    print("HPS - SineWith20Harmonics 700Hz")
    print("Without octave trick: " + getPitchInfo(HPS(signalGenerator.getSineWithHarmonics(700,2048,44100,20), 44100, False, 4, octaveTrick=False)))
    print("With octave trick:    " + getPitchInfo(HPS(signalGenerator.getSineWithHarmonics(700,2048,44100,20), 44100, False, 4, octaveTrick=True)))
    print()

    print()

    print("CASES TO BE MAINTAINED")
    print("HPS - Triangle 600Hz")
    print("Without octave trick: " + getPitchInfo(HPS(signalGenerator.getTriangle(600,2048,44100), 44100, False, 4, octaveTrick=False)))
    print("With octave trick:    " + getPitchInfo(HPS(signalGenerator.getTriangle(600,2048,44100), 44100, False, 4, octaveTrick=True)))
    print()

    print("HPS - Sine 500Hz")
    print("Without octave trick: " + getPitchInfo(HPS(signalGenerator.getSine(500,2048,44100), 44100, False, 4, octaveTrick=False)))
    print("With octave trick:    " + getPitchInfo(HPS(signalGenerator.getSine(500,2048,44100), 44100, False, 4, octaveTrick=True)))
    print()

    print("HPS - Square 40000Hz")
    print("Without octave trick: " + getPitchInfo(HPS(signalGenerator.getSquare(4000,2048,44100), 44100, False, 4, octaveTrick=False)))
    print("With octave trick:    " + getPitchInfo(HPS(signalGenerator.getSquare(4000,2048,44100), 44100, False, 4, octaveTrick=True)))
    print()

def customFFTTest1():
    signal = signalGenerator.getSine(440,2048,44100)
    npBins = fft(signal, False)
    customBins = fft(signal, True)
    # print(npBins.shape())
    print(len(npBins), len(customBins))
    for i in range(3):
        print(npBins[i], customBins[i])
    for i in range(3):
        print(npBins[-i], customBins[-i])

def customFFTTest2(freqs = [50,100,500,1000,5000,10000]):
    for freq in freqs:
        sine = signalGenerator.getSine(freq, 1024, 44100)
        square = signalGenerator.getSquare(freq, 1024, 44100)
        saw = signalGenerator.getSaw(freq, 1024, 44100)
        triangle = signalGenerator.getTriangle(freq, 1024, 44100)
        sineHarmonics = signalGenerator.getSineWithHarmonics(freq, 1024, 44100, 15)

        signals = {"sine" : sine, "square" : square, "saw" : saw, "triangle" : triangle, "sineHarmonics" : sineHarmonics}

        for signalType in signals:

            signal = signals[signalType]

            print("%s %sHz" % (signalType, freq))

            start1 = timer()
            pred1 = naiveFT(signal, 44100, False)
            end1 = timer()

            start2 = timer()
            pred2 = naiveFT(signal, 44100, True)
            end2 = timer()

            print("naiveFT numpy vs CustomFFT:  %sHz (%ss)    %sHz (%ss)" % ('{:.4f}'.format(pred1).rjust(12), str(end1-start1).rjust(22,"0"), '{:.4f}'.format(pred2).rjust(12), str(end2-start2).rjust(22,"0")))

            ####

            start1 = timer()
            pred1 = cepstrum(signal, 44100, False)
            end1 = timer()

            start2 = timer()
            pred2 = cepstrum(signal, 44100, True)
            end2 = timer()

            print("Cepstrum numpy vs CustomFFT: %sHz (%ss)    %sHz (%ss)" % ('{:.4f}'.format(pred1).rjust(12), str(end1-start1).rjust(22,"0"), '{:.4f}'.format(pred2).rjust(12), str(end2-start2).rjust(22,"0")))

            ####

            start1 = timer()
            pred1 = HPS(signal, 44100, False, 4)
            end1 = timer()

            start2 = timer()
            pred2 = HPS(signal, 44100, True, 4)
            end2 = timer()

            print("HPS numpy vs CustomFFT:      %sHz (%ss)    %sHz (%ss)" % ('{:.4f}'.format(pred1).rjust(12), str(end1-start1).rjust(22,"0"), '{:.4f}'.format(pred2).rjust(12), str(end2-start2).rjust(22,"0")))

            print()

def signalGainTest1():
    print("SINE 440Hz")
    signal = signalGenerator.getSine(440, 22050, 44100)
    print("min: %s   max: %s   %s percent clipped" % (min(signal), max(signal), proportionClipping(signal)*100))
    sf.write("wavs/gainTests/440sine.wav", signal, 44100)

    print("\nQUARTER GAIN")
    signal = multiplyGain(signal, 0.25)
    print("min: %s   max: %s   %s percent clipped" % (min(signal), max(signal), proportionClipping(signal)*100))
    sf.write("wavs/gainTests/440sineQuarterGain.wav", signal, 44100)

    print("\nADD WHITE NOISE")
    signal = addGaussianWhiteNoise(signal, 0.002)
    print("min: %s   max: %s   %s percent clipped" % (min(signal), max(signal), proportionClipping(signal)*100))
    sf.write("wavs/gainTests/440sineQuarterGainWithNoise.wav", signal, 44100)

    print("BOOST GAIN UNTIL CLIP")
    signal = multiplyGainUntilClipping(signal)
    print("min: %s   max: %s   %s percent clipped" % (min(signal), max(signal), proportionClipping(signal)*100))
    sf.write("wavs/gainTests/440sineQuarterGainWthNoiseBoosted.wav", signal, 44100)
    
    print("DOUBLE GAIN")
    signal = multiplyGain(signal, 2)
    print("min: %s   max: %s   %s percent clipped" % (min(signal), max(signal), proportionClipping(signal)*100))
    sf.write("wavs/gainTests/440sineQuarterGainWthNoiseBoostedTwice.wav", signal, 44100)

    print("DOUBLE GAIN (again)")
    signal = multiplyGain(signal, 2)
    print("min: %s   max: %s   %s percent clipped" % (min(signal), max(signal), proportionClipping(signal)*100))
    sf.write("wavs/gainTests/440sineQuarterGainWthNoiseBoostedThrice.wav", signal, 44100)
    
def phaseVocoderTest1():
    # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    # sf.write("wavs/phaseVocoderTests/440sineWithHarmonics.wav", signal, 44100)
    
    # stretched = phaseVocoderStretch(signal, 44100, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # sf.write("wavs/phaseVocoderTests/440sineWithHarmonicsStretched.wav", stretched, 44100)

    # shifted = phaseVocoderPitchShift(signal, 44100, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # sf.write("wavs/phaseVocoderTests/880sineWithHarmonicsHopefully.wav", shifted, 44100)


    signal, sampleRate = sf.read("wavs/uhhh-gentle-female-singing_B_major.wav")
    signal = toMono(signal)
    # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    sf.write("wavs/phaseVocoderTests/female-ooh.wav", signal, sampleRate)
    
    stretched = phaseVocoderStretch(signal, sampleRate, 2**(4/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write("wavs/phaseVocoderTests/female-oohStretched.wav", stretched, sampleRate)

    shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(4/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write("wavs/phaseVocoderTests/female-oohShiftedHopefully.wav", shifted, sampleRate)
    
    
    signal, sampleRate = sf.read("wavs/bruh.wav")
    signal = toMono(signal)
    # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    sf.write("wavs/phaseVocoderTests/bruh.wav", signal, sampleRate)
    
    stretched = phaseVocoderStretch(signal, sampleRate, 2**(4/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write("wavs/phaseVocoderTests/bruhStretched.wav", stretched, sampleRate)

    shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(4/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write("wavs/phaseVocoderTests/bruhShiftedHopefully.wav", shifted, sampleRate)
    

    # signal, sampleRate = sf.read("wavs/wee.wav")
    # signal = toMono(signal)
    # # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    # sf.write("wavs/phaseVocoderTests/wee.wav", signal, sampleRate)
    
    # stretched = phaseVocoderStretch(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # sf.write("wavs/phaseVocoderTests/weeStretched.wav", stretched, sampleRate)

    # shifted = phaseVocoderPitchShift(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # print("shifting done")
    # sf.write("wavs/phaseVocoderTests/weeShiftedHopefully.wav", shifted, sampleRate)


    # signal, sampleRate = sf.read("wavs/guitarC3 cropped.wav")
    # signal = toMono(signal)
    # # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    # sf.write("wavs/phaseVocoderTests/guitarC3 cropped.wav", signal, sampleRate)
    
    # stretched = phaseVocoderStretch(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # sf.write("wavs/phaseVocoderTests/guitarC3 croppedStretched.wav", stretched, sampleRate)

    # shifted = phaseVocoderPitchShift(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # print("shifting done")
    # sf.write("wavs/phaseVocoderTests/guitarC3 croppedShiftedHopefully.wav", shifted, sampleRate)

    
    # signal, sampleRate = sf.read("wavs/clar.wav")
    # # signal = toMono(signal) #already mono
    # # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    # sf.write("wavs/phaseVocoderTests/clar.wav", signal, sampleRate)
    
    # # stretched = phaseVocoderStretch(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # # sf.write("wavs/phaseVocoderTests/guitarC3 croppedStretched.wav", stretched, sampleRate)

    # shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(-12/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    # print("shifting done")
    # sf.write("wavs/phaseVocoderTests/clarShiftedHopefully.wav", shifted, sampleRate)


    # signal, sampleRate = sf.read("wavs/bowlc6.wav")
    # signal = toMono(signal) #already mono
    # # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    # sf.write("wavs/phaseVocoderTests/bowlc6.wav", signal, sampleRate)
    
    # # stretched = phaseVocoderStretch(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # # sf.write("wavs/phaseVocoderTests/guitarC3 croppedStretched.wav", stretched, sampleRate)

    # shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(1/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    # print("shifting done")
    # sf.write("wavs/phaseVocoderTests/bowlc6ShiftedHopefully.wav", shifted, sampleRate)

    # # # wavs/instrumentSamples/LABSPiano/LABSPianoA4.wav
    # signal, sampleRate = sf.read("wavs/instrumentSamples/LABSPiano/LABSPianoA4.wav")
    # signal = toMono(signal) #already mono
    # # signal = signalGenerator.getSineWithHarmonics(440, 2048*100, 44100,25)
    # sf.write("wavs/phaseVocoderTests/LABSPianoA4C4.wav", signal, sampleRate)
    
    # # stretched = phaseVocoderStretch(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
    # # sf.write("wavs/phaseVocoderTests/guitarC3 croppedStretched.wav", stretched, sampleRate)

    # shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(2/12), 2048, 1792, windowFunction=getHanningWindow(2048))
    # print("shifting done")
    # sf.write("wavs/phaseVocoderTests/LABSPianoA4C4ShiftedHopefully.wav", shifted, sampleRate)

def phaseVocoderTest2():
    signal, sampleRate = sf.read("wavs/clar.wav")
    sf.write("wavs/phaseVocoderTests/phasinessTest/clar.wav", signal, sampleRate)

    stretched = phaseVocoderStretch(signal, sampleRate, 2**(1/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write("wavs/phaseVocoderTests/phasinessTest/clarStretched.wav", stretched, sampleRate)
    
    shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(1/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    print("shifting done")
    sf.write("wavs/phaseVocoderTests/phasinessTest/clarShiftedUp.wav", shifted, sampleRate)


    compressed = phaseVocoderStretch(signal, sampleRate, 2**(-1/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write("wavs/phaseVocoderTests/phasinessTest/clarCompressed.wav", compressed, sampleRate)

    shifted = phaseVocoderPitchShift(signal, sampleRate, 2**(-1/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    print("shifting done")
    sf.write("wavs/phaseVocoderTests/phasinessTest/clarShiftedDown.wav", shifted, sampleRate)

def generalPhaseVocoderTest(inFolderPath, inFileName, outFolderPath, shiftFactor):
    signal, sampleRate = sf.read(inFolderPath + inFileName)
    if sf.info(inFolderPath + inFileName).channels > 1:
        signal = toMono(signal)
    sf.write(outFolderPath + inFileName, signal, sampleRate)

    stretched = phaseVocoderStretch(signal, sampleRate, shiftFactor, 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write(outFolderPath + inFileName[:-4] + "stretched.wav", stretched, sampleRate)
    
    shifted = phaseVocoderPitchShift(signal, sampleRate, shiftFactor, 2048, 1536, windowFunction=getHanningWindow(2048))
    sf.write(outFolderPath + inFileName[:-4] + "shifted.wav", shifted, sampleRate)

def phaseVocoderTest3():
    files = ["clar.wav", "bowlc6.wav", "uhhh-gentle-female-singing_B_major.wav", "choir-boy-solo-singing_150bpm_D_minor.wav"]
    inFolderPath = "wavs/"
    outFolderPath = "wavs/PVTest2/"
    
    for f in files:
        generalPhaseVocoderTest(inFolderPath, f, outFolderPath, 2**(4/12))
        print(f + " done.")

def pitchMatchingTest1():
    hanningWindow = getHanningWindow(2048)

    filename = "uhhh-gentle-female-singing_B_major.wav"
    # filename = "clar_stretched.wav"
    # filename = "choir-boy-solo-singing_150bpm_D_minor.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp1 = PitchProfile("wavs/" + filename, sampleRate, "HPS", {"isCustomFFT" : False, "numDownsamples":4}, "voice", 2048, 1024, hanningWindow, "female-ooh")
    pp1.analysePitch()

    pp1.writeLog("wavs/pitchMatchTest/original.log")

    pp1.autoCorrectPitchData()
    pp1.writeLog("wavs/pitchMatchTest/correctedData.log")

    # signal, sampleRate = sf.read("wavs/" + filename)
    # shifted = phaseVocoderPitchShift(toMono(signal), sampleRate, 2**(7.5/12), 2048, 1536, windowFunction=getHanningWindow(2048))
    # filename = "choir-boy-solo-singing_150bpm_D_minor_detuned.wav"
    # sf.write("wavs/" + filename, shifted, sampleRate)

    sampleRate = sf.info("wavs/" + filename).samplerate
    pp2 = PitchProfile("wavs/" + filename, sampleRate, "HPS", {"isCustomFFT" : False, "numDownsamples":4}, "voice", 2048, 1024, hanningWindow, "choirboy")
    pp2.analysePitch()

    # signal = matchPitch(pp2, pp1)
    # sf.write("wavs/pitchMatchTest/matched.wav", signal, sampleRate)
    
    signal = matchPitch(pp2, pp1)
    sf.write("wavs/pitchMatchTest/corrected.wav", signal, sampleRate)

    filename = "pitchMatchTest/corrected.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp3 = PitchProfile("wavs/" + filename, sampleRate, "HPS", {"isCustomFFT" : False, "numDownsamples":4}, "voice", 2048, 1024, hanningWindow, "choirboy")
    pp3.analysePitch()
    pp3.writeLog("wavs/pitchMatchTest/correctedAudio.log")


    ### now to make the choir boy sound like the female singer (insofar as melody is concerned)

    filename = "choir-boy-solo-singing_150bpm_D_minor.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp4 = PitchProfile("wavs/" + filename, sampleRate, "HPS", {"isCustomFFT" : False, "numDownsamples":4}, "voice", 2048, 1024, hanningWindow, "choirboy")
    pp4.analysePitch()
    pp4.writeLog("wavs/pitchMatchTest/toMatch_Audio.log")

    signal = matchPitch(pp4, pp1)
    sf.write("wavs/pitchMatchTest/matched.wav", signal, sampleRate)

    filename = "pitchMatchTest/matched.wav"
    sampleRate = sf.info("wavs/" + filename).samplerate
    pp5 = PitchProfile("wavs/" + filename, sampleRate, "HPS", {"isCustomFFT" : False, "numDownsamples":4}, "voice", 2048, 1024, hanningWindow, "choirboy")
    pp5.analysePitch()
    pp5.writeLog("wavs/pitchMatchTest/matchedAudio.log")

def cepstrumTweakingTest():
    signal = signalGenerator.getSquare(900,2048,44100)
    print(cepstrum(signal, 44100, False, expectedMin=300, expectedMax=1500))
    print(cepstrum(signal, 44100, True, expectedMin=300, expectedMax=1500))

    signal = signalGenerator.getSquare(1500,2048,44100)
    print(cepstrum(signal, 44100, False, expectedMin=500, expectedMax=3000))
    print(cepstrum(signal, 44100, True, expectedMin=500, expectedMax=3000))

def naiveFTWithPhaseTest(freqs = [50,100,200,300,400,440,500,800,1000,2000,4000,8000,10000,15000]):
    for freq in freqs:
        sine = signalGenerator.getSine(freq, 1280, 44100)
        square = signalGenerator.getSquare(freq, 1280, 44100)
        saw = signalGenerator.getSaw(freq, 1280, 44100)
        triangle = signalGenerator.getTriangle(freq, 1280, 44100)
        sineHarmonics = signalGenerator.getSineWithHarmonics(freq, 1280, 44100, 15)

        signals = {"sine":sine, "square":square, "saw":saw, "triangle":triangle, "sineHarmonics":sineHarmonics}

        for signal in signals:
            start = timer()
            pred = naiveFTWithPhase(signals[signal], 44100, False)
            end = timer()
            print("%s   %sHz: %sHz (zerocross)       - took %ss" % (signal, freq, pred, end-start))

            start = timer()
            pred = naiveFT(signals[signal[:1024]], 44100, False)
            end = timer()
            print("%s   %sHz: %sHz (zerocross)       - took %ss\n " % (signal, freq, pred, end-start))

# naiveFTWithPhaseTest()


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


# signal, sampleRate = sf.read("wavs/clar.wav")
# stretched = phaseVocoderStretch(signal, sampleRate, 2, 2048, 1536, windowFunction=getHanningWindow(2048))
# sf.write("wavs/clar_stretched.wav", stretched, sampleRate)
    