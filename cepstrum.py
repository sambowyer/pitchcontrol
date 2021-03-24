import fft
import math
import numpy as np 
import matplotlib.pyplot as plt

CUSTOM_FFT = False

def fft(signal):
    if CUSTOM_FFT:
        return fft.fft(signal)
    else:
        return np.fft.rfft(signal)

def ifft(signal):
    if CUSTOM_FFT:
        return fft.ifft(signal)
    else:
        return np.fft.ifft(signal)

def magnitudeSquaredBins(bins):
    return [abs(i)*abs(i) for i in bins]

def cepstrumPredict(signal, sampleRate):
    # plt.subplot(2, 1, 1)
    # plt.plot(range(len(signal)), signal)

    freq_vector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    log_X = np.log(np.abs((fft(signal))))

    maxLog = max(log_X)
    print(freq_vector[np.where(log_X == maxLog)])

    cepstrumBins = np.abs(fft(log_X))
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
    print(maxBin, quefrencies[maxBin])
    # plt.show()
    return 1/quefrencies[maxBin]
    # return sampleRate/maxBin
