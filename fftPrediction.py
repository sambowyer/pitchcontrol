import fft
import numpy as np


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
    mags = np.abs((fft(signal))))

    maxLog = max(log_X)
    return freq_vector[np.where(log_X == maxLog)])