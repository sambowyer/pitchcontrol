import sys, getopt, math, logging, argparse
from predict import zerocross, autocorrelation, AMDF, naiveFT, naiveFTWithPhase, cepstrum, HPS
from helpers import getPitchInfo, getMedian, getTrimmedMean, getHanningWindow, toMono
import pitchShift
from PitchProfile import PitchProfile
import numpy as np
from timeit import default_timer as timer
import soundfile as sf

helpMessage = '''pitchcontrol.py usage
    pitchcontrol [-cdms] [inputFile] (matchingFile) [outputFile] (numSemitones)

-c  --correct   Apply pitch correction to the input file.
-d  --detect    Detect the pitch of the input file with all detection algorithms.
-h  --help      Print this usage information to output.
-m  --match     Shift the input file to match the melody in a 'matching' file.
-s  --shift     Shift the input file by a specified number of semitones.
'''

def main():
    args = sys.argv[1:]

    if len(args) == 0:
        print(helpMessage)

    elif args[0] in ("-d", "--detect") and len(args) == 2:
        detectPitch(args[1])

    elif args[0] in ("-c", "--correct") and len(args) == 3:
        correctPitch(args[1], args[2])

    elif args[0] in ("-m", "--match") and len(args) == 4:
        matchPitch(args[1], args[2], args[3])

    elif args[0] in ("-s", "--shift") and len(args) == 4:
        shift(args[1], args[2], float(args[3]))

    else:
        print(helpMessage)


def detectPitch(file):
    predictions = []
    executionTimes = []

    signal, sampleRate = sf.read(file, always_2d=True)
    signal = toMono(signal)

    start = timer()
    pred = zerocross(signal, sampleRate)
    end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("zerocross:        %s     (took %ss)" % (getPitchInfo(pred, True), end-start))

    
    if len(signal) > 1024:
        start = timer()
        pred = autocorrelation(signal[:1024], sampleRate)
        end = timer()
    else:
        start = timer()
        pred = autocorrelation(signal, sampleRate)
        end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("autocorrelation:  %s    (took %ss)" % (getPitchInfo(pred, True), end-start))

    if len(signal) > 1024:
        start = timer()
        pred = AMDF(signal[:1024], sampleRate)
        end = timer()
    else:
        start = timer()
        pred = AMDF(signal, sampleRate)
        end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("AMDF:             %s     (took %ss)" % (getPitchInfo(pred, True), end-start))

    start = timer()
    pred = naiveFT(signal, sampleRate, True)
    end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("naiveFT:          %s     (took %ss)" % (getPitchInfo(pred, True), end-start))

    start = timer()
    pred = naiveFTWithPhase(signal, sampleRate, True)
    end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("naiveFTWithPhase: %s     (took %ss)" % (getPitchInfo(pred, True), end-start))

    start = timer()
    pred = cepstrum(signal, sampleRate, True)
    end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("cepstrum:         %s     (took %ss)" % (getPitchInfo(pred, True), end-start))

    start = timer()
    pred = HPS(signal, sampleRate, True, 2)
    end = timer()
    predictions.append(pred)
    executionTimes.append(end-start)
    print("HPS:              %s     (took %ss)" % (getPitchInfo(pred, True), end-start))

    
    print("median:           %s     (took %ss)" % (getPitchInfo(getMedian(predictions), True), sum(executionTimes)))

    print("mean of middle 3: %s     (took %ss)" % (getPitchInfo(getTrimmedMean(predictions, 2/7), True), sum(executionTimes)))

def correctPitch(inputFile, outputFile):
    sampleRate = sf.info(inputFile).samplerate
    pp = PitchProfile(inputFile, sampleRate, "naiveFT", {"isCustomFFT" : True}, blockSize=4096, overlap=0)
    pp.analysePitch()
    # pp.printLog()
    newSignal = pitchShift.correctPitch(pp)
    sf.write(outputFile, newSignal, sampleRate)

def matchPitch(inputFile, matchingFile, outputFile):
    sampleRateIn = sf.info(inputFile).samplerate
    sampleRateMatching = sf.info(matchingFile).samplerate
    if sampleRateIn != sampleRateMatching:
        print("Input file and matching file must have the same sample rate.")
        return

    pp1 = PitchProfile(inputFile, sampleRateIn, "naiveFTWithPhase", {"isCustomFFT" : True}, blockSize=8192, overlap=0)
    pp1.analysePitch()
    # print(pp1.pitchData)
    # pp1.printLog()
    pp2 = PitchProfile(matchingFile, sampleRateIn, "naiveFTWithPhase", {"isCustomFFT" : True}, blockSize=8192, overlap=0)
    pp2.analysePitch()
    # print(pp2.pitchData)
    # pp2.printLog()

    newSignal = pitchShift.matchPitch(pp1, pp2)
    sf.write(outputFile, newSignal, sampleRateIn)

def shift(inputFile, outputFile, numSemitones):
    signal, sampleRate = sf.read(inputFile, always_2d=True)
    signal = toMono(signal)

    newSignal = pitchShift.phaseVocoderPitchShift(signal, sampleRate, 2**(numSemitones/12), windowLength=2048, overlapLength=1536, windowFunction=getHanningWindow(2048))
    sf.write(outputFile, newSignal, sampleRate)


if __name__ == "__main__":
    main()