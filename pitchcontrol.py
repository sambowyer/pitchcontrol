import sys
import wave
from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS
from helpers import *
import signalGenerator
import math
import numpy as np
from timeit import default_timer as timer
import soundfile as sf
import logging
import sys

verbose = False

def analysePitch(file):
    if(verbose):
        logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    buffer = circularBuffer(CHUNK_SIZE)
    data, samplerate = sf.read(file)

    data = toMono(data)

    rms = [sf.blocks('myfile.wav', blocksize=1024, overlap=512)]

    predictions = []

    for i in range(CHUNK_SIZE):
        buffer.add(data[i])




