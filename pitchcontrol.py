import sys
import wave
from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS
from helpers import *
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

def analysePitch(file):
    buffer = circularBuffer(CHUNK_SIZE)
    data, samplerate = sf.read(file)

    data = toMono(data)

    rms = [sf.blocks('myfile.wav', blocksize=1024, overlap=512)]

    predictions = []

    for i in range(CHUNK_SIZE):
        buffer.add(data[i])




