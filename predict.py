import customFFT
import math, cmath
from helpers import resample, getTrimmedMean, getMidiNoteWithCents, fft
import numpy as np 
import matplotlib.pyplot as plt #for bug fixing and testing

#### TIME-DOMAIN ALGORITHMS

def zerocross(signal, sampleRate):
    '''Zero-Crossing Pitch Detection
    Predicts the frequency of a mono signal by estimating the average period given by points where the signal changes sign (-ve/+ve).'''

    firstZeroCrossIndex = -1
    lastZeroCrossIndex = len(signal)
    zeroCrossCount = 0
    isPositive = (signal[0] > 0)

    for index, sample in enumerate(signal):
        if (sample > 0) != isPositive:
            zeroCrossCount += 1
            isPositive = not isPositive

            if firstZeroCrossIndex == -1:
                firstZeroCrossIndex = index
            else:
                lastZeroCrossIndex = index

    return sampleRate*0.5*(zeroCrossCount-1)/(lastZeroCrossIndex-firstZeroCrossIndex)

def autocorrelation(signal, sampleRate, expectedMin=20, expectedMax=20000):
    '''Autocorrelation Pitch Detection
    Predicts the frequency of a mono signal by finding the time interval (of m samples) for which the signal most consistently repeats itself.
    Autocorrelation uses the product of signal values at intervals of m samples to find this optimal m.'''

    maxComparisionDistance = len(signal) // 2

    #each mth bin corresponds to the autocorrelation sum:- sum of x(i)x(i+m) forall i
    bins = [0 for i in range(maxComparisionDistance+1)]
    binCounts = [0 for i in range(maxComparisionDistance+1)]

    for signalIndex in range(len(signal)):
        for m in range(1, maxComparisionDistance+1):
            sum = 0
            counter = 0

            
            i = 1
            while (signalIndex + i * m) < len(signal):
                sum += signal[signalIndex] * signal[signalIndex + i*m]
                counter += 1
                binCounts[m] += 1

                i += 1

            bins[m] += sum

    maxCorrelation = -float("inf")
    maxM = 1
    for m in range(max(1, math.ceil(sampleRate/expectedMax)), min(maxComparisionDistance+1, math.ceil(sampleRate/expectedMin))):
        if bins[m] > maxCorrelation:
            maxCorrelation = bins[m]
            maxM = m

    return sampleRate / maxM

def AMDF(signal, sampleRate, b=1, expectedMin=20, expectedMax=20000):
    '''Average Magnitude Differential Function Pitch Detection
    Predicts the frequency of a mono signal by finding the time interval (of m samples) for which the signal most consistently repeats itself.
    AMDF uses the Euclidean distance (to the power of b) between signal values at intervals of m samples to find this optimal m.'''

    maxComparisionDistance = len(signal) // 2

    #each mth bin corresponds to the autocorrelation sum:- sum of x(i)x(i+m) forall i
    bins = [0 for i in range(maxComparisionDistance+1)]
    binCounts = [0 for i in range(maxComparisionDistance+1)]

    for signalIndex in range(len(signal)):
        for m in range(1, maxComparisionDistance+1):
            sum = 0
            counter = 0

            
            i = 1
            while (signalIndex + i * m) < len(signal):
                sum += (abs(signal[signalIndex] - signal[signalIndex + i*m]))**b
                counter += 1
                binCounts[m] += 1

                i += 1

            bins[m] += sum

    # print(bins)
    minCorrelation = bins[1]/binCounts[1]
    minM = 1
    for m in range(max(1, math.ceil(sampleRate/expectedMax)), min(maxComparisionDistance+1, math.ceil(sampleRate/expectedMin))):
        if bins[m]/binCounts[m] < minCorrelation:
            minCorrelation = bins[m]/binCounts[m]
            minM = m

    return sampleRate / minM

#### FREQUENCY-DOMAIN ALGORITHMS

def naiveFT(signal, sampleRate, isCustomFFT, expectedMin=20, expectedMax=20000):
    '''A Naive Fourier-Transform Pitch Detection Method
    Predicts the frequency of a mono signal simply by picking the largest peak in the  Fourier-transform of the signal.'''

    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    minExpectedBin = min(np.where(freq_vector >= expectedMin)[0])
    maxExpectedBin = max(np.where(freq_vector <= expectedMax)[0])

    mags = np.abs(fft(signal, isCustomFFT))

    maxMag = 0
    maxMagBin = 1
    for i in range(max(1, minExpectedBin), min(len(mags), maxExpectedBin+1)):
        if mags[i] > maxMag:
            maxMag = mags[i]
            maxMagBin = i

    return freq_vector[maxMagBin]

    # freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    # mags = np.abs(fft(signal, isCustomFFT))
    # maxLog = max(mags)
    # print(np.where(mags == maxLog)[0])
    # return freq_vector[np.where(mags == maxLog)][0]

def naiveFTWithPhase(signal, sampleRate, isCustomFFT, expectedMin=20, expectedMax=20000):
    '''Another Naive Fourier Transform approach where phase information is used to tweak the predition.
    Compute two overlapping fourier transforms and initially just choose the bin with the largest magnitude (in the second FT frame) - exactly the same as naiveFT.
    Then, use the phase information to tweak the prediction with an improved resolution. 
    This is the same method by which true-bin-frequenies are calculated in the phase vocoder implementation.'''
    #First find the ideal FT window size (should be a power of 2), assuming a 75% overlap in the two windows.
    windowLength = 2**(math.floor(math.log2(len(signal)*0.8)))
    print(windowLength)
    freq_vector = np.fft.rfftfreq(windowLength, d=1/sampleRate)
    minExpectedBin = min(np.where(freq_vector >= expectedMin)[0])
    maxExpectedBin = max(np.where(freq_vector <= expectedMax)[0])

    #Then get our two FT frames
    bins1 = fft(signal[:windowLength], isCustomFFT)
    bins2 = fft(signal[windowLength//4:windowLength+windowLength//4], isCustomFFT)

    mags = np.abs(bins2)

    maxMag = 0
    maxMagBin = 1
    for i in range(max(1, minExpectedBin), min(len(mags), maxExpectedBin+1)):
        if mags[i] > maxMag:
            maxMag = mags[i]
            maxMagBin = i

    #Now to utilise the phase information
    deltaT_in = (windowLength//4)/sampleRate
    phaseDiff = cmath.phase(bins2[maxMagBin]) - cmath.phase(bins1[maxMagBin])

    numCyclesToTrueFreq = round(deltaT_in*freq_vector[maxMagBin] - phaseDiff/(2*math.pi))
    trueFreq = (phaseDiff + 2*math.pi*numCyclesToTrueFreq)/(2*math.pi*deltaT_in)

    return trueFreq

def cepstrum(signal, sampleRate, isCustomFFT, expectedMin=20, expectedMax=20000):
    '''Cepstrum Pitch Detection
    Predicts the frequency of a mono signal by finding the period which most strongly correlates to the distance between peaks in the Fourier-transform of the signal.
    Assuming the peaks in the Fourier transform are located at harmonics of the signal, this period should represent the distance between the harmonics, i.e. the fundamental period.'''

    # plt.subplot(2, 1, 1)
    # plt.plot(range(len(signal)), signal)

    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    mags = np.abs(fft(signal, isCustomFFT))
    log_X = []

    #to supress potential (very rare) numpy warnings that come with some particular signals (e.g. a 900Hz square wave w/ length 2048 and sample rate 44100Hz) -
    #   not strictly necessary but leads to a better UX
    if 0 in mags: 
        for i in range(len(mags)):
            if mags[i] == 0:
                log_X.append(-float("inf"))
            else:
                log_X.append(np.log(mags[i]))
    else:
        #faster processing possible in this case and no need to worry about warnings
        log_X = np.log(mags)

    # maxLog = max(log_X)
    # print(freq_vector[np.where(log_X == maxLog)])

    cepstrumBins = np.abs(fft(log_X, isCustomFFT))
    quefrencies = np.fft.rfftfreq(len(log_X), d=freq_vector[1]-freq_vector[0])

    # print(cepstrumBins)
    # print(quefrencies)
    # print(len(cepstrumBins))
    # print(len(quefrencies))

    # plt.subplot(2, 1, 2)
    # plt.plot(quefrencies[1:], cepstrumBins[1:])
    # plt.plot(range(len(cepstrumBins)-1), cepstrumBins[1:])

    minExpectedBin = min(np.where(quefrencies >= 1/expectedMax)[0])
    maxExpectedBin = max(np.where(quefrencies <= 1/expectedMin)[0])
    
    maxBin = max(5, minExpectedBin)
    maxValue = 0
    for i in range(max(5, minExpectedBin), min(len(cepstrumBins), maxExpectedBin+1)):
        if cepstrumBins[i] > maxValue and cepstrumBins[i] < float("inf"):
            maxValue = cepstrumBins[i]
            maxBin = i
    # print(maxBin, quefrencies[maxBin])
    # plt.show()
    return 1/quefrencies[maxBin]
    # return sampleRate/maxBin

def HPS(signal, sampleRate, isCustomFFT, numDownsamples, expectedMin=20, expectedMax=20000, octaveTrick=False):
    '''Harmonic Product Spectrum Pitch Detection
    Predicts the frequency of a mono signal by first computing (the magnitudes within) its Fourier-transform and then resampling (downsampling) this by factors of 1/2, 1/3, 1/4, etc. .
    Then we may multiply these downsampled versions and can expect a peak correlating to the fundamental frequency of the original signal.'''
    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    minExpectedBin = min(np.where(freq_vector >= expectedMin)[0])
    maxExpectedBin = max(np.where(freq_vector <= expectedMax)[0])
    mags = np.abs(fft(signal, isCustomFFT))

    resampledSpectra = [resample(mags, sampleRate, sampleRate/i) for i in range(1 ,numDownsamples+1)]

    for spectrum in resampledSpectra:
        for i in range(len(mags)):
            if i >= len(spectrum):
                break
            mags[i] *= spectrum[i]

    maxMag = 0
    maxMagBin = 1
    for i in range(max(1, minExpectedBin), min(len(mags), maxExpectedBin+1)):
        if mags[i] > maxMag:
            maxMag = mags[i]
            maxMagBin = i

    #ocassionaly HPS predicts an octave too high, so if the second highest peak is at approximately half the frequency of the highest (that is, an octave below)
    #and the ratio of magnitudes between these two highest peaks is above 1/(2*numDownsamples), then predict the lower octave instead
    # This trick is far from 100% effective in reducing octave errors but does prove useful in some cases
    if octaveTrick: 
        maxMag2 = 0
        maxMag2Bin = 1
        for i in range(max(1, minExpectedBin), min(len(mags), maxExpectedBin+1)):
            if mags[i] > maxMag2 and i != maxMagBin:
                maxMag2 = mags[i]
                maxMag2Bin = i

        # print(maxMag / maxMag)

        # allow for 50 cent leeway either side of the true octave below the highest peak
        if abs(getMidiNoteWithCents(freq_vector[maxMagBin]) - getMidiNoteWithCents(2*freq_vector[maxMag2Bin])) <= 0.5 and maxMag2/maxMag >= 0.1:
            return freq_vector[maxMag2Bin]

    return freq_vector[maxMagBin]


#### Functions utilising all pitch detection algorithms

## Function to return a dictionary of predictions from all algorithms
def getAllPredictions(signal, sampleRate, b, isCustomFFT, numDownsamples):
    predictions = {"zerocross" : zerocross(signal, sampleRate), 
                   "autocorrelation" : autocorrelation(signal, sampleRate), 
                   "AMDF" : AMDF(signal, sampleRate, b), 
                   "naiveFT" : naiveFT(signal, sampleRate, isCustomFFT),
                   "naiveFTWithPhase" : naiveFTWithPhase(signal, sampleRate, isCustomFFT),
                   "cepstrum" : cepstrum(signal, sampleRate, isCustomFFT), 
                   "HPS" : HPS(signal, sampleRate, isCustomFFT, numDownsamples)}
    
    return predictions

def getTrimmedMeanPrediction(signal, sampleRate, b, isCustomFFT, numDownsamples, trimSize):
    predictions = [zerocross(signal, sampleRate), autocorrelation(signal, sampleRate), AMDF(signal, sampleRate, b),
        naiveFT(signal, sampleRate, isCustomFFT), naiveFTWithPhase(signal, sampleRate, isCustomFFT), 
        cepstrum(signal, sampleRate, isCustomFFT), HPS(signal, sampleRate, isCustomFFT, numDownsamples)]
    return getTrimmedMean(predictions, trimSize)
