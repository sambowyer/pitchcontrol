from helpers import *
import math, cmath
import numpy as np 

def phase(a):
    phase = cmath.phase(a)
    return phase

def phaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, windowFunction=None):
    if windowFunction == None:
        windowFunction = [1 for i in range(windowLength)]

    hopIn = windowLength - overlapLength
    hopOut = round(hopIn * scalingFactor)
    deltaT_in = hopIn/sampleRate
    deltaT_out= hopOut/sampleRate

    numFrames = ((len(signal)-windowLength)//(hopIn)) +1
    finalFrameStartIndex = hopIn * (numFrames-1)
    frameStartIndex = 0

    newSignal = [0 for i in range((numFrames)*hopOut+windowLength)]

    freq_vector = np.fft.fftfreq(windowLength, d=1/sampleRate)

    #analysis of first frame
    bins = np.fft.rfft([signal[frameStartIndex+i]*windowFunction[i] for i in range(windowLength)])
    phaseIn = [phase(a) for a in bins]
    phaseOut = phaseIn
    #synthesis of first frame (no changes made)
    for i in range(frameStartIndex, frameStartIndex+windowLength):
        newSignal[i] += signal[i]

    #now for the analysis and synthesis of all other frames
    for numFrame in range(1,numFrames):
        frameStartIndex += windowLength-overlapLength
        prevPhaseIn = phaseIn
        prevPhaseOut = phaseOut

        bins = np.fft.rfft([signal[frameStartIndex+i]*windowFunction[i] for i in range(windowLength)])

        phaseIn = [phase(a) for a in bins]
        phaseOut = []

        for i in range(len(bins)):
            # best explanation of phase issues/solutions seems to be https://sethares.engr.wisc.edu/vocoders/Transforms.pdf Section 5.3.4 'The Phase Vocoder'
            numCyclesToTrueFreq = round(deltaT_in*freq_vector[i] - (phaseIn[i] - prevPhaseIn[i])/(2*math.pi))
            trueFreq = (phaseIn[i] - prevPhaseIn[i] + 2*math.pi*numCyclesToTrueFreq)/(2*math.pi*deltaT_in)
            newPhase = prevPhaseOut[i] + 2*math.pi*trueFreq*deltaT_in

            phaseOut.append(newPhase)
            bins[i] = abs(bins[i])*(math.e**(1j*newPhase))

        newPartialSignal = np.fft.irfft(bins)

        for i in range(windowLength):
            newSignal[i+numFrame*hopOut] += newPartialSignal[i]

    if proportionClipping(newSignal) > 0:
        newSignal = multiplyGainUntilClipping(newSignal)

    return newSignal

def phaseVocoderPitchShift(signal, sampleRate, scalingFactor, windowLength, overlapLength, windowFunction=None):
    newSignal = phaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, windowFunction)
    return resample(newSignal, sampleRate, sampleRate/scalingFactor)

def matchPitch(originalPitchProfile, matchingPitchProfile):
    '''Takes the signal from *originalPitchProfile* and shifts it in various ways so that the returned signal has a pitch profile that 
    matches that of *matchingPitchProfile
    NOTE: Requires both pitch profiles to use the same sampleRate'''
    #get list of major sections where pitch stays stable in each pitchProfile
    #iterate through the profiles and for each new intersection of the above sections calculate the corresponding pitch ratio
    #   -> then use phase vocoder pitch shift on each of these intersections so that the new pitch profile matches the desired profile
    originalIndexedPitchData = originalPitchProfile.getIndexedPitchData()
    matchingIndexedPitchData = matchingPitchProfile.getIndexedPitchData()

    original sections

    #compress both indexedPitchData lists into 'sections' where the pitch stays 'stable' i.e. stays within +/-10 cents of the section's starting pitch
    originalSectionStartPitch = originalPitchProfile[0][2]
    originalSectionStartIndex = 0
    matchingSectionStartPitch = matchingPitchProfile[0][2]
    originalSectionStartIndex = 0
    i = 1
    while i < min(len(originalIndexedPitchData), len(matchingIndexedPitchData)):
        if abs(getMidiNoteWithCents(originalIndexedPitchData[i][2]) - getMidiNoteWithCents(originalSectionStartPitch)) <= 0.1:
            del originalIndexedPitchData[i]
            originalIndexedPitchData[originalSectionStartIndex][1] += originalPitchProfile.blockSize - originalPitchProfile.overlap
            i -= 1
        else:
            originalSectionStartPitch = originalIndexedPitchData[i][2]
            originalSectionStartIndex += 1

        if abs(getMidiNoteWithCents(matchingIndexedPitchData[i][2]) - getMidiNoteWithCents(matchingSectionStartPitch)) <= 0.1:
            del matchingIndexedPitchData[i]
            matchingIndexedPitchData[matchingSectionStartIndex][1] += matchingPitchProfile.blockSize - matchingPitchProfile.overlap
            i -= 1
        else:
            matchingSectionStartPitch = matchingIndexedPitchData[i][2]
            matchingSectionStartIndex += 1

        i += 1

    #for each intersection of the newly found 'stable sections' we must now shift the frequency of the original signal to match the matching signal's frequency