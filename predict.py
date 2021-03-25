
import fft
import math
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

def autocorrelation(signal, sampleRate):
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

    maxCorrelation = 0
    maxM = 0
    for m in range(1, maxComparisionDistance+1):
        if bins[m] >  maxCorrelation:
            maxCorrelation = bins[m]
            maxM = m

    return sampleRate / maxM

def AMDF(signal, sampleRate, b=1):
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
    for m in range(2, maxComparisionDistance+1):
        if bins[m]/binCounts[m] <  minCorrelation:
            minCorrelation = bins[m]/binCounts[m]
            minM = m

    return sampleRate / minM

#### FREQUENCY-DOMAIN ALGORITHMS

## Preliminary sunctions for frequency-domain algorithms

def fft(signal, isCustomFFT):
    if isCustomFFT:
        return fft.fft(signal)
    else:
        return np.fft.rfft(signal)

def ifft(isCustomFFT):
    if isCustomFFT:
        return fft.ifft(signal)
    else:
        return np.fft.ifft(signal)

def magnitudeSquaredBins(bins):
    return [abs(i)*abs(i) for i in bins]

def linearInterpolate(x1, x2, gamma):
    return (x1 + (x2-x1)*gamma)

def resample(signal, oldSampleRate, newSampleRate):
    resampledSignal = []
    for i in range(len(signal)):
        resampleIndex = i*oldSampleRate/newSampleRate
        if resampleIndex >= len(signal) - 1:
            break
        resampledSignal.append(linearInterpolate(signal[math.floor(resampleIndex)], signal[math.ceil(resampleIndex)], resampleIndex % 1))

    return resampledSignal


## Prediction Functions

def naiveFT(signal, sampleRate, isCustomFFT):
    '''A Naive Fourier-Transform Pitch Detection Method
    Predicts the frequency of a mono signal simply by picking the largest peak in the  Fourier-transform of the signal.'''

    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    mags = np.abs(fft(signal, isCustomFFT))
    maxLog = max(mags)
    return freq_vector[np.where(mags == maxLog)][0]

def cepstrum(signal, sampleRate, isCustomFFT):
    '''Cepstrum Pitch Detection
    Predicts the frequency of a mono signal by finding the period which most strongly correlates to the distance between peaks in the Fourier-transform of the signal.
    Assuming the peaks in the Fourier transform are located at harmonics of the signal, this period should represent the distance between the harmonics, i.e. the fundamental period.'''

    # plt.subplot(2, 1, 1)
    # plt.plot(range(len(signal)), signal)

    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    log_X = np.log(np.abs(fft(signal, isCustomFFT)))

    maxLog = max(log_X)
    # print(freq_vector[np.where(log_X == maxLog)])

    cepstrumBins = np.abs(fft(log_X, isCustomFFT))
    quefrencies = np.fft.rfftfreq(log_X.size, d=freq_vector[1]-freq_vector[0])

    # print(cepstrumBins)
    # print(quefrencies)
    # print(len(cepstrumBins))
    # print(len(quefrencies))

    # plt.subplot(2, 1, 2)
    # plt.plot(quefrencies[1:], cepstrumBins[1:])
    # plt.plot(range(len(cepstrumBins)-1), cepstrumBins[1:])
    
    maxBin = 0
    maxValue = 0
    for b, val in enumerate(cepstrumBins):
        if val > maxValue and b>5:
            maxValue = val
            maxBin = b
    # print(maxBin, quefrencies[maxBin])
    # plt.show()
    return 1/quefrencies[maxBin]
    # return sampleRate/maxBin

def HPS(signal, sampleRate, isCustomFFT, numDownsamples):
    '''Harmonic Product Spectrum Pitch Detection
    Predicts the frequency of a mono signal by first computing (the magnitudes within) its Fourier-transform and then resampling (downsampling) this by factors of 1/2, 1/3, 1/4, etc. .
    Then we may multiply these downsampled versions and can expect a peak correlating to the fundamental frequency of the original signal.'''
    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    mags = np.abs(fft(signal, isCustomFFT))

    resampledSpectra = [resample(mags, sampleRate, sampleRate/i) for i in range( 1,numDownsamples+1)]

    for spectrum in resampledSpectra:
        for i in range(len(mags)):
            if i >= len(spectrum):
                break
            mags[i] *= spectrum[i]

    maxBin = 0
    maxValue = 0
    for b, val in enumerate(mags):
        if val > maxValue:
            maxValue = val
            maxBin = b

    return freq_vector[maxBin]


#### Functions utilising all pitch detection algorithms

## Preliminary function

def getTrimmedMean(data, trimSize):
    '''returns the mean of the list 'data' excluding its smallest and largest elements.
    The total proportion of the list to be excluded from the mean calculation is given by 'trimSize' - between 0 and 1.'''
    if trimSize > 1:
        return sum
    sortedData = data.copy()
    sortedData.sort()
    trimIndices = [math.floor((len(data)-1)*trimSize), math.ceil((len(data)-1)*(1-trimSize))]
    trimIndices.sort()
    return sum(sortedData[trimIndices[0]:trimIndices[1]])/(trimIndices[1]-trimIndices[0])


## Function to return a dictionary of predictions from all algorithms

def getAllPredictions(signal, sampleRate, b, isCustomFFT, numDownsamples):
    predictions = {"zerocross" : zerocross(signal, sampleRate), 
                   "autocorrelation" : autocorrelation(signal, sampleRate), 
                   "AMDF" : AMDF(signal, sampleRate, b), 
                   "naiveFFT" : naiveFFT(signal, sampleRate, isCustomFFT), 
                   "cepstrum" : cepstrum(signal, sampleRate, isCustomFFT), 
                   "HPS" : HPS(signal, sampleRate, isCustomFFT, numDownsamples)}
    
    return predictions

def getTrimmedMeanPrediction(signal, sampleRate, b, isCustomFFT, numDownsamples, trimSize):
    predictions = [zerocross(signal, sampleRate), autocorrelation(signal, sampleRate), AMDF(signal, sampleRate, b),
        naiveFFT(signal, sampleRate, isCustomFFT), cepstrum(signal, sampleRate, isCustomFFT), HPS(signal, sampleRate, isCustomFFT, numDownsamples)]
    return getTrimmedMean(predictions, trimSize)