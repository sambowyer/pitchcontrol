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

# printPitchInfo(zerocross(signalGenerator.getSineWithHarmonics(880,2048,22050, 20), 44100))
# printPitchInfo(autocorrelation(signalGenerator.getSineWithHarmonics(880,2048,22050, 20), 44100))
# printPitchInfo(AMDF(signalGenerator.getSineWithHarmonics(880,2048,22050, 20), 44100))
# printPitchInfo(naiveFT(signalGenerator.getSineWithHarmonics(880,2048,22050, 20), 44100, False))
# printPitchInfo(cepstrum(signalGenerator.getSineWithHarmonics(880,2048,22050, 20), 44100, False))
# printPitchInfo(HPS(signalGenerator.getSineWithHarmonics(880,2048,22050, 20), 44100, False, 4))


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