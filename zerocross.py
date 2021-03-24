def zerocrossPredict(signal, sampleRate):
    '''Predicts the frequency of a mono signal by estimating the average period given by points where the signal changes sign (-ve/+ve).'''

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