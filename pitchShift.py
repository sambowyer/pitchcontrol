from helpers import toMono, proportionClipping, multiplyGain, multiplyGainUntilClipping, resample, getMidiNoteWithCents, getMedian, getHanningWindow
import math, cmath
import numpy as np 
import soundfile as sf
from copy import deepcopy

def phase(a):
    phase = cmath.phase(a)
    return phase

def phaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, windowFunction=None):
    if len(signal) < windowLength:
        print("ERROR") #CHANGE THIS SO IT ACTUALLY THROWS AN ERROR
        return signal
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
    # print(windowLength, len(signal))
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

def phaseVocoderPitchShift(signal, sampleRate, scalingFactor, windowLength=2048, overlapLength=1536, windowFunction=None, forceConstantLength=False):
    newSignal = phaseVocoderStretch(signal, sampleRate, scalingFactor, windowLength, overlapLength, windowFunction)
    newSignal = resample(newSignal, sampleRate, sampleRate/scalingFactor)
    if forceConstantLength:
        return phaseVocoderStretch(newSignal, sampleRate, len(signal)/len(newSignal), windowLength, overlapLength, windowFunction)
    else:
        return newSignal

def compressIndexedPitchData(indexedPitchData):
    sectionStartPitch = indexedPitchData[0][2]

    i = 1
    while i < len(indexedPitchData):
        if abs(getMidiNoteWithCents(indexedPitchData[i][2]) - getMidiNoteWithCents(sectionStartPitch)) <= 0.25:
            indexedPitchData[i-1][1] = indexedPitchData[i][1]
            indexedPitchData
            del indexedPitchData[i]
            i -= 1
        else:
            sectionStartPitch = indexedPitchData[i][2]
        i += 1

def compressIndexedPitchData2(indexedPitchData):
    currentSectionPitches = [indexedPitchData[0][2]]
    deviatingPitches = []
    sectionPitch = indexedPitchData[0][2]
    compressedPitchData = []

    sectionStartIndex = indexedPitchData[0][0]
    sectionEndIndex = indexedPitchData[0][1]

    numDeviatingEstimates = 0

    i = 1

    while i < len(indexedPitchData):
        # print(i)
        freqDiff = abs(getMidiNoteWithCents(indexedPitchData[i][2]) - getMidiNoteWithCents(sectionPitch))
        if freqDiff <= 0.25 or abs(freqDiff - 12) <= 0.25:
            currentSectionPitches.append(indexedPitchData[i][2])
            sectionEndIndex = indexedPitchData[i][1]

            numDeviatingEstimates = 0
            
            if len(currentSectionPitches) % 2 == 0:
                sectionPitch = getMedian(currentSectionPitches[1:])
            else:
                sectionPitch = getMedian(currentSectionPitches)

        else:
            numDeviatingEstimates += 1
            deviatingPitches.append(indexedPitchData[i][2])

            if numDeviatingEstimates >= 3:
                compressedPitchData.append([sectionStartIndex, sectionEndIndex, sectionPitch])
                currentSectionPitches = [deviatingPitches[0]]
                sectionPitch = deviatingPitches[0]
                deviatingPitches = []

                sectionStartIndex = indexedPitchData[i-3][0]
                sectionEndIndex = indexedPitchData[i-3][1]

                numDeviatingEstimates = 0
                i -= 2

        i += 1

    compressedPitchData.append([sectionStartIndex, sectionEndIndex, sectionPitch])

    return compressedPitchData
            
def removeShortSections(indexedPitchData, minAcceptableSectionLength):
    i=1
    while i < len(indexedPitchData):
        if indexedPitchData[i][1] - indexedPitchData[i][0] < minAcceptableSectionLength:
            indexedPitchData[i-1][1] = indexedPitchData[i][1]
            del indexedPitchData[i]
            i -= 1
        i += 1


def matchPitch(originalPitchProfile, matchingPitchProfile):
    '''Takes the signal from *originalPitchProfile* and shifts it in various ways so that the returned signal has a pitch profile that 
    matches that of *matchingPitchProfile
    NOTE: Requires both pitch profiles to use the same sampleRate'''
    #get list of major sections where pitch stays stable in each pitchProfile
    #iterate through the profiles and for each new intersection of the above sections calculate the corresponding pitch ratio
    #   -> then use phase vocoder pitch shift on each of these intersections so that the new pitch profile matches the desired profile
    originalIndexedPitchData = originalPitchProfile.getIndexedPitchData()
    matchingIndexedPitchData = matchingPitchProfile.getIndexedPitchData()

    #compress both indexedPitchData lists into 'sections' where the pitch stays 'stable' i.e. stays within +/-10 cents of the section's starting pitch
    # compressIndexedPitchData(originalIndexedPitchData)
    # compressIndexedPitchData(matchingIndexedPitchData)

    originalIndexedPitchData = compressIndexedPitchData2(originalIndexedPitchData)
    matchingIndexedPitchData = compressIndexedPitchData2(matchingIndexedPitchData)

    removeShortSections(originalIndexedPitchData, 3*originalPitchProfile.blockSize//2 + 1)
    removeShortSections(matchingIndexedPitchData, 3*matchingPitchProfile.blockSize//2 + 1)

    # print(originalIndexedPitchData, matchingIndexedPitchData)

    newSignal = []
    isMono = sf.info(originalPitchProfile.location).channels == 1
    analysisWindowLength = originalPitchProfile.blockSize//2
    overlap = 3*analysisWindowLength//4

    #for each intersection of the newly found 'stable sections' we must now shift the frequency of the original signal to match the matching signal's frequency
    intersectionStartIndex = 0
    intersectionEndIndex = 0
    originalSectionCount = 0
    matchingSectionCount = 0

    while originalSectionCount < len(originalIndexedPitchData) or matchingSectionCount < len(matchingIndexedPitchData):
        if originalSectionCount == len(originalIndexedPitchData):
            break #reached the end of the original signal
        elif matchingSectionCount == len(matchingIndexedPitchData):
            newSignal += toMono(sf.read(originalPitchProfile.location, start=intersectionStartIndex, always_2d=True)[0])
            break #reached the end of the matching signal - no more pitch shifting needs to take place
        else:
            scalingFactor = matchingIndexedPitchData[matchingSectionCount][2]/originalIndexedPitchData[originalSectionCount][2]

            if originalIndexedPitchData[originalSectionCount][1] < matchingIndexedPitchData[matchingSectionCount][1]:
                # print("o")
                intersectionEndIndex = originalIndexedPitchData[originalSectionCount][1]
                originalSectionCount += 1
            elif originalIndexedPitchData[originalSectionCount][1] > matchingIndexedPitchData[matchingSectionCount][1]:
                # print("m")
                intersectionEndIndex = matchingIndexedPitchData[matchingSectionCount][1]
                matchingSectionCount += 1
            else: #equality is only case left
                # print("om")
                intersectionEndIndex = originalIndexedPitchData[originalSectionCount][1]
                originalSectionCount += 1
                matchingSectionCount += 1
            # print("o:%s/%s  m:%s/%s" % (originalSectionCount, len(originalIndexedPitchData), matchingSectionCount, len(matchingIndexedPitchData)))
            partialSignal, sampleRate = sf.read(originalPitchProfile.location, start=intersectionStartIndex, stop=intersectionEndIndex)
            
            if isMono == False:
                partialSignal = toMono(partialSignal)
            
            shiftedIntersection = phaseVocoderPitchShift(partialSignal, sampleRate, scalingFactor, windowLength=analysisWindowLength, overlapLength=overlap, windowFunction=getHanningWindow(analysisWindowLength), forceConstantLength=True)
            # print(len(shiftedIntersection), len(partialSignal), intersectionEndIndex-intersectionStartIndex)
            newSignal += shiftedIntersection

            intersectionStartIndex = intersectionEndIndex

    
    return newSignal

def correctPitch(originalPitchProfile, correctNotes=None):
    correctedPitchProfile = deepcopy(originalPitchProfile)
    correctedPitchProfile.autoCorrectPitchData(correctNotes)

    return matchPitch(originalPitchProfile, correctedPitchProfile)
