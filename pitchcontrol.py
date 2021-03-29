import sys
import wave
from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS
import signalGenerator
import math
import circularBuffer
import numpy as np
from timeit import default_timer as timer

import soundfile as sf

#lowest possible frequency detection (realistically) is around sampleRate/CHUNK_SIZE
#so if CHUNK_SIZE=1024 and sampleRate=44.1kHz, we can detect (hopefully) from about 43Hz upwards
#We want CHUNK_SIZE to be a power of 2 to maximise the efficiency of the FFT
CHUNK_SIZE = 1024

def toMono(signal):
    if type(signal[0] == list):
        return [sum(channels) for channels in signal]

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

def analysePitch(file):
    buffer = circularBuffer(CHUNK_SIZE)
    data, samplerate = sf.read(file)

    data = toMono(data)

    rms = [sf.blocks('myfile.wav', blocksize=1024, overlap=512)]

    predictions = []

    for i in range(CHUNK_SIZE):
        buffer.add(data[i])


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

expectedIntervalTest()

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

# generatedSignalsTest()