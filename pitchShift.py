from helpers import *
import math, cmath
import customFFT
import numpy as np 

def phase(a):
    phase = cmath.phase(a)
    # if phase < 0:
    #     phase += 2*math.pi
    return phase

def changePhase(a, newPhase):
    return abs(a)*(math.e ** ((0+1j)*newPhase))

def unitStep(x):
    if x < 0:
        return 0
    else:
        return 1

def fullFFT(signal, isCustomFFT):
    if isCustomFFT:
        bins = customFFT.fft(signal)
    else:
        bins = np.fft.rfft(signal)
    return bins + bins[::-1]

def fullIFFT(bins, isCustomFFT):
    if isCustomFFT:
        signal = customFFT.ifft(bins)
    else:
        signal = np.fft.irfft(bins[:len(bins)//2])
    return signal

def phaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT = False, windowFunction=None):
    #Condsider each element of this array as a 'frame' of the signal
    stft_in = STFT(signal, windowLength, overlapLength, isCustomFFT, windowFunction)
    freq_vector = np.fft.rfftfreq(windowLength, d=1/sampleRate)

    hop_In = windowLength - overlapLength
    hop_Out = hop_In * scalingFactor

    deltaT_in = hop_In / sampleRate
    deltaT_out = hop_Out / sampleRate

    trueBinFrequencies = [stft_in[0]]

    for frameIndex in range(1, len(stft_in)):
        trueBinFrequencies.append([])
        for binIndex in range(len(stft_in[frameIndex])):
            freqShift = ((phase(stft_in[frameIndex][binIndex]) - phase(stft_in[frameIndex-1][binIndex])) / deltaT_in) - freq_vector[binIndex]
            trueFreq = freq_vector[binIndex] + ((freqShift + math.pi) % 2*math.pi) - math.pi 
            trueBinFrequencies[frameIndex].append(trueFreq)

    newPhases = [[phase(x) for x in stft_in[0]]]

    for frameIndex in range(1, len(stft_in)):
        newPhases.append([])
        for binIndex in range(len(stft_in[frameIndex])):
            newPhase = newPhases[frameIndex-1] + deltaT_out * trueBinFrequencies[frameIndex][binIndex]
            newPhases[frameIndex].append(newPhase)

    stft_out = [stft_in[0]]

    for frameIndex in range(1, len(stft_in)):
        stft_out.append([])
        for binIndex in range(len(stft_in[frameIndex])):
            stft_out[frameIndex].append(changePhase(stft_in[frameIndex][binIndex], newPhases[frameIndex][binIndex]))

    inverse_stft_out = [ifft(window, isCustomFFT) for window in stft_out]

    newSignal = []
    newSignalIndex = 0
    newSignalFinished = False

    for newSignalIndex in range(math.floor(len(signal) * scalingFactor)):
        newSignalPointValue = 0
        for frameIndex, frame in enumerate(inverse_stft_out):
            precedingFrameIndex = newSignalIndex - frameIndex*hop_out
            newSignalPointValue += frame[newSignalIndex - frameIndex*hop_out]*(unitStep(precedingFrameIndex) - unitStep(precedingFrameIndex - windowLength))

    return newSignal
    
def addPartialNewSignal(newSignal, frameStartIndex, freq_vector, hopIn, hopOut, numFrame, signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT = False, windowFunction=None):
    if windowFunction == None:
        windowFunction = [1 for i in range(windowLength)]
    if frameStartIndex <= 0:
        print("fin recursion",frameStartIndex,numFrame)
        # bins = fft([signal[frameStartIndex+i]*windowFunction[i] for i in range(windowLength)], isCustomFFT, True)
        bins = np.fft.rfft([signal[frameStartIndex+i]*windowFunction[i] for i in range(windowLength)])
        # print(bins[5])
        phaseIn = [phase(a) for a in bins]
        # phaseIn = [0 for a in bins]
        for i in range(frameStartIndex, frameStartIndex+windowLength):
            newSignal[i] += signal[i]
        return phaseIn, phaseIn
    else:
        prevPhaseIn, prevPhaseOut = addPartialNewSignal(newSignal, frameStartIndex-hopIn, freq_vector, hopIn, hopOut, numFrame-1, signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT, windowFunction)
        # bins = fft([signal[frameStartIndex+i]*windowFunction[i] for i in range(windowLength)], isCustomFFT, True)
        bins = np.fft.rfft([signal[frameStartIndex+i]*windowFunction[i] for i in range(windowLength)])

        deltaT_in = hopIn/sampleRate
        deltaT_out= hopOut/sampleRate

        # print(len(bins))
        # print(numFrame)
        phaseIn = [phase(a) for a in bins]
        phaseOut = []

        for i in range(len(bins)):
            # trueFreq = freq_vector[i] + ((((phaseIn[i] - prevPhaseIn[i]) / deltaT_in) - freq_vector[i] + math.pi) % (2*math.pi)) - math.pi
            # newPhase = prevPhaseOut[i] + trueFreq*deltaT_out

            
            trueFreqPrediction = (phaseIn[i] - prevPhaseIn[i])/(2*math.pi*deltaT_in)
            newPrediction = trueFreqPrediction
            below = trueFreqPrediction < freq_vector[i]
            n=0
            while below == True:
                newPrediction = trueFreqPrediction + 1/deltaT_in
                if newPrediction > freq_vector[i]:
                    below = False
                else:
                    trueFreqPrediction = newPrediction
                    n += 1
            if freq_vector[i] - trueFreqPrediction < newPrediction - freq_vector[i]:
                trueFreq = trueFreqPrediction
            else:
                trueFreq = newPrediction
                n += 1
            newPhase = prevPhaseOut[i] + 2*math.pi*trueFreq*deltaT_in + (abs(n-i)%2)*math.pi


            ### BEST
            # trueFreq = (phaseIn[i] - prevPhaseIn[i] + 2*math.pi*i)/(2*math.pi*(hopIn/sampleRate))
            # newPhase = (prevPhaseOut[i] + 2*math.pi*trueFreq*(hopIn/sampleRate)) + ((i+1)%2)*math.pi


            # extraPhase = phaseIn[i] - prevPhaseIn[i] - 2*math.pi*hopIn*i/windowLength
            # extraPhase -= round(extraPhase/(2*math.pi))*2*math.pi
            # extraPhase = (extraPhase+2*math.pi*hopIn*i/windowLength)*scalingFactor
            # newPhase = prevPhaseOut[i] + extraPhase

            # numCyclesToTrueFreq = round(deltaT_in*freq_vector[i] - (phaseIn[i] - prevPhaseIn[i])/(2*math.pi))
            # trueFreq = (phaseIn[i] - prevPhaseIn[i] + 2*math.pi*numCyclesToTrueFreq)/(2*math.pi*deltaT_in)
            # newPhase = prevPhaseOut[i] + 2*math.pi*trueFreq*deltaT_in

            #2nd best zynaptiq
            # trueFreq = (sampleRate/windowLength)*(i + phaseIn[i]*(windowLength/overlapLength)/(2*math.pi))
            # newPhase = (prevPhaseOut[i] + 2*math.pi*trueFreq*(hopIn/sampleRate)) + (i%2)*math.pi
            # newPhase = prevPhaseOut[i] + trueFreq*deltaT_in

            phaseOut.append(newPhase)
            # bins[i] = changePhase(bins[i], newPhase)
            bins[i] = abs(bins[i])*(math.e**(1j*newPhase))

        newPartialSignal = np.fft.irfft(bins)
        # newPartialSignal = [newPartialSignal[i]*windowFunction[i] for i in range(windowLength)]
        # for i in range(windowLength):
        #     if windowFunction[i] != 0:
        #         newPartialSignal[i] /= windowFunction[i]
        # newPartialSignal = ifft(bins, isCustomFFT, True)
        # print(len(newPartialSignal), newPartialSignal[0])
        # print(frameStartIndex)
        # print(len(newSignal))
        # print(frameStartIndex,frameStartIndex+windowLength)
        # print(frameStartIndex+numFrame*(hopOut - hopIn), frameStartIndex+numFrame*(hopOut - hopIn)+windowLength)
        for i in range(frameStartIndex, frameStartIndex + windowLength):
            
            newSignal[i+numFrame*(hopOut - hopIn)] += newPartialSignal[i%windowLength]
            # newSignal[i] += abs(newPartialSignal[i%windowLength])

        return phaseIn, phaseOut


def RECURSIVEphaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT=False, windowFunction=None):
    hopIn = windowLength - overlapLength
    hopOut = round(hopIn * scalingFactor)

    numFrames = ((len(signal)-windowLength)//(hopIn)) +1
    # print("numframes", numFrames)
    finalFrameStartIndex = hopIn * (numFrames-1)
    newSignal = [0 for i in range(math.ceil(len(signal)*scalingFactor))]
    # print(len(newSignal))
    freq_vector = np.fft.fftfreq(windowLength, d=1/sampleRate)
    # freq_vector = [i/sampleRate for i in range(windowLength)]

    addPartialNewSignal(newSignal, finalFrameStartIndex, freq_vector, hopIn, hopOut, numFrames-1, signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT, windowFunction)

    # return multiplyGainUntilClipping([abs(x)*phase(x) for x in newSignal])
    print(proportionClipping(newSignal))
    print(min(newSignal), max(newSignal))
    if proportionClipping(newSignal) > 0:
        newSignal = multiplyGainUntilClipping(newSignal)
    print(min(newSignal), max(newSignal))
    return newSignal

def stretch(sound_array, f, window_size, h):
    """ Stretches the sound by a factor `f` """

    phase  = np.zeros(window_size)
    hanning_window = np.hanning(window_size)
    result = [0+0j for i in range(len(sound_array) *f + window_size)] #np.zeros( len(sound_array) //f + window_size)

    for i in np.arange(0, len(sound_array)-(window_size+h), h*f):

        # two potentially overlapping subarrays
        a1 = sound_array[i: i + window_size]
        a2 = sound_array[i + h: i + window_size + h]

        # resynchronize the second array on the first
        s1 =  np.fft.fft(hanning_window * a1)
        s2 =  np.fft.fft(hanning_window * a2)
        phase = (phase + np.angle(s2/s1)) % 2*np.pi
        a2_rephased = np.fft.ifft(np.abs(s2)*np.exp(1j*phase))

        # add to result
        i2 = int(i/f)
        result[i2 : i2 + window_size] += hanning_window*a2_rephased

    result = ((2**(16-4)) * result/max(result)) # normalize (16bit)

    return result.astype('int16')

def phaseVocoderPitchShift(signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT = False, windowFunction=None):
    newSignal = RECURSIVEphaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, isCustomFFT, windowFunction)
    # newSignal = stretch(signal, scalingFactor, windowLength, windowLength-overlapLength)
    print("signalmade")
    return resample(newSignal, sampleRate, sampleRate/scalingFactor)
    # return newSignal[::2]
