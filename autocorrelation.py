def autocorrelationPredict(signal, sampleRate):
    '''Predicts the frequency of a mono signal by estimating the average wavelength given by points where the signal changes sign (-ve/+ve).'''

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