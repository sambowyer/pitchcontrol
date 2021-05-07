import matplotlib.pyplot as plt 
import soundfile as sf
import numpy as np
from helpers import toMono, resample, clipSignal, getHanningWindow
import signalGenerator
from cmath import phase
import customFFT
import pitchShift, PitchProfile
import pickle

def timeDomain():
    # flute, sampleRate = toMono(sf.read("wavs/instrumentSamples/BBCFlute/BBCFluteA4.wav"))
    t = np.arange(0.0, 0.025, 0.00001)
    s = np.sin(440 * np.pi * t)

    fig, ax = plt.subplots()
    # Move left y-axis and bottim x-axis to centre, passing through (0,0)
    # ax.spines['left'].set_position('center')
    # ax.spines['bottom'].set_position('center')

    # Eliminate upper and right axes
    # ax.spines['right'].set_color('none')
    # ax.spines['top'].set_color('none')

    # Show ticks in the left and lower axes only
    # ax.xaxis.set_ticks_position('bottom')
    # ax.yaxis.set_ticks_position('left')

    ax.plot(t, s)

    ax.set(xlabel='Time (s)', ylabel='Amplitude',
        title='Time Domain Representation of a 440Hz Sine Wave')
    # ax.grid()

    fig.savefig("../report/images/timedomain.png")
    plt.show()

# timeDomain()

def basicFFT():
    # signal, sampleRate = toMono(sf.read("wavs/instrumentSamples/BBCFlute/BBCFluteA4.wav"))
    sampleRate = 44100
    signal1 = signalGenerator.getSine(400, 2048, sampleRate)
    signal2 = signalGenerator.getSine(600, 2048, sampleRate)
    signal = [2*signal1[i] + signal2[i] for i in range(2048)]
    
    freqVector = np.fft.fftfreq(len(signal), d=1/sampleRate)
    fft = np.fft.fft(signal)

    print(max(np.sqrt(np.abs(fft))))
    print(np.sqrt(np.abs(fft))[1800: 2100])

    fig, ax = plt.subplots()
    ax.plot(freqVector, np.sqrt(np.abs(fft)))

    ax.set(xlabel='Frequency (Hz)', ylabel='Magnitude',
        title='Example Fourier Transform Magnitudes')
    # ax.grid()
    ax.set_xlim([-1000, 1000])
    ax.set_ylim([0, 40])

    fig.savefig("../report/images/FFTMags.png")
    plt.show()

    fig, ax = plt.subplots()
    ax.plot(freqVector, [phase(x) for x in fft])

    ax.set(xlabel='Frequency (Hz)', ylabel='Magnitude',
        title='Example Fourier Transform Phases')
    # ax.grid()
    ax.set_xlim([-1000, 1000])
    # ax.set_ylim([0, 1600])

    fig.savefig("../report/images/FFTPhases.png")
    plt.show()

# basicFFT()

def cepstrum():
    signal, sampleRate = sf.read("wavs/instrumentSamples/BBCFlute/BBCFluteA4.wav")
    signal = [a+b for [a, b] in signal[10000:12048]]
    
    freqVector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    fft = customFFT.fft(signal)

    fig, ax = plt.subplots()
    ax.plot(freqVector, np.abs(fft))
    plt.xticks((list([440*i for i in range(7)])))
    ax.set_xlim([0, 3000])
    ax.set(xlabel='Frequency (Hz)', ylabel='Magnitude', title='FFT Magnitudes of a Flute A5 Note (440Hz)')
    
    # ax.grid()

    fig.savefig("../report/images/fluteA5FFT.png")
    plt.show()

    logX = np.log(np.abs(fft))

    fig, ax = plt.subplots()
    ax.plot(freqVector, logX)
    plt.xticks((list([440*i for i in range(7)])))
    ax.set_xlim([0, 3000])
    ax.set(xlabel='Frequency (Hz)', ylabel='Magnitude', title='Logarithm of FFT Magnitudes of a Flute A5 Note (440Hz)')
    # ax.grid()

    fig.savefig("../report/images/fluteA5FFTlog.png")
    plt.show()


    quefrencies = np.fft.rfftfreq(len(logX), d=freqVector[1]-freqVector[0])

    fig, ax = plt.subplots()
    ax.plot(quefrencies, np.abs(customFFT.fft(logX)))
    plt.xticks(list(plt.xticks()[0]).remove(0.005))
    plt.xticks((list([0, 1/440, 1/220])))
    ax.set_xlim([0, 0.0065])
    ax.set_ylim([0, 500])

    ax.set(xlabel='Quefrency (1/Hz)', ylabel='Magnitude', title='Cepstrum of a Flute A5 Note (440Hz)')
    # ax.grid()

    fig.savefig("../report/images/fluteA5Cepstrum.png")
    plt.show()

# cepstrum()
    
def HPS():
    signal, sampleRate = sf.read("wavs/instrumentSamples/BBCFlute/BBCFluteA4.wav")
    signal = [a+b for [a, b] in signal[10000:12048]]

    resampledSignals = [resample(signal, sampleRate, sampleRate/i) for i in range(1,5)]
    fftsMags = [customFFT.fft(sig) for sig in resampledSignals]
    print(len(resampledSignals), len(fftsMags[0]))

    for n in range(0,4):
        for i in range(len(fftsMags[n]), len(fftsMags[0])):
            fftsMags[n].append(0)

    fftsMags[0].append(0)
    fftsMags[1].append(0)
    fftsMags[2].append(0)
    fftsMags[3].append(0)

    for i in range(len(fftsMags)):
        fftsMags[i] = np.abs(fftsMags[i])

    freqVector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    print(len(freqVector))
    
    PS = [1 for i in range(1+len(fftsMags[0]))]
    for i in range(4):
        for j in range(len(fftsMags[i])):
            print(i,j)
            PS[j] *= fftsMags[i][j]

    PS = PS[:-1]

    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)
    fig.suptitle('HPS for a Flute A5 (440Hz) Note (sample rate = 44100Hz)')

    ax1.plot(freqVector, fftsMags[0])
    ax1.set_ylabel('Magnitude')
    ax1.set_xlabel('Frequency')
    ax1.set_title('The Original Signal')
    plt.sca(ax1)
    plt.xticks((list([440*i for i in range(7)])))
    ax1.set_xlim([0, 3000])
    print(1)

    ax2.plot(freqVector, fftsMags[1])
    ax2.set_ylabel('Magnitude')
    ax2.set_xlabel('Frequency')
    ax2.set_title('Downsampled by a factor of 2')
    plt.sca(ax2)
    plt.xticks((list([440*i for i in range(7)])))
    ax2.set_xlim([0, 3000])
    print(1)

    ax3.plot(freqVector, fftsMags[2])
    ax3.set_ylabel('Magnitude')
    ax3.set_xlabel('Frequency')
    ax3.set_title('Downsampled by a factor of 3')
    plt.sca(ax3)
    plt.xticks((list([440*i for i in range(7)])))
    ax3.set_xlim([0, 3000])
    print(1)

    ax4.plot(freqVector, fftsMags[3])
    ax4.set_ylabel('Magnitude')
    ax4.set_xlabel('Frequency')
    ax4.set_title('Downsampled by a factor of 4')
    plt.sca(ax4)
    plt.xticks((list([440*i for i in range(7)])))
    ax4.set_xlim([0, 3000])
    print(1)

    ax5.plot(freqVector, PS)
    ax5.set_ylabel('Magnitude')
    ax5.set_xlabel('Frequency')
    ax5.set_title('The Product Spectrum')
    plt.sca(ax5)
    plt.xticks((list([440*i for i in range(7)])))
    ax5.set_xlim([0, 3000])
    print(1)

    plt.subplots_adjust(hspace=2)

    fig.savefig("../report/images/fluteA5HPS.png")
    plt.show()

# HPS()

def stretchResample():
    ticks = np.arange(0.0, 2048/44100, 1/44100)
    sine = signalGenerator.getSine(440, 2048, 441000)
    # sineHalf = [sine[2*i] for i in range(len(sine)//2)]
    sineHalf = resample(sine, 44100, 22050)

    fig, (ax1, ax2) = plt.subplots(2, 1)

    # plt.subplot(2, 1, 1)
    ax1.plot(ticks, sine)#, 'o-')
    ax1.set_title('Original 440Hz sine wave (sample rate = 44100Hz)')
    ax1.set_xlabel('Time (s)')
    ax1.set_xlim([0, 2048/44100])


    # plt.subplot(2, 1, 2)
    ax2.plot(ticks[:len(sineHalf)], sineHalf)#, '.-')
    ax2.set_title('Resampled at 22050Hz')
    ax2.set_xlabel('Time (s)')
    ax2.set_xlim([0, 2048/44100])

    plt.subplots_adjust(hspace=1)


    fig.savefig("../report/images/strecthResample.png")
    fig.show()

stretchResample()

def powerLeakage():
    signal, sampleRate = sf.read("wavs/instrumentSamples/BBCTrumpet/BBCTrumpetG5.wav")
    signal = [a+b for [a, b] in signal[10000:12048]]
    
    freqVector = np.fft.rfftfreq(len(signal), d=1/sampleRate)
    fft = np.abs(customFFT.fft(signal))

    

    fig, ax = plt.subplots()
    plt.figure(figsize=[3.6, 4.8])
    ax.bar(["Bin 36: 775Hz", "Bin 37: 796Hz"], [fft[36], fft[37]])
    # ax.plot(freqVector, np.abs(fft))
    # plt.xticks([775,784,796])
    # ax.set_xlim([400, 1100])
    ax.set(xlabel='Frequency Bins', ylabel='Magnitude', title='FFT Magnitudes of a Trumpet G5 Note (784Hz)')
    # ax.grid()

    

    fig.savefig("../report/images/trumpetG4PowerLeakage.png")
    plt.show()

# powerLeakage()

def clipping():
    ticks = np.arange(0.0, 2048/44100, 1/44100)
    sine = signalGenerator.getSine(440, 2048, 441000)
    sine = [x*1.2 for x in sine]
    # sineHalf = [sine[2*i] for i in range(len(sine)//2)]
    clipped = sine.copy()
    clipSignal(clipped)

    fig, (ax1, ax2) = plt.subplots(2, 1)

    # plt.subplot(2, 1, 1)
    ax1.plot(ticks, sine)#, 'o-')
    ax1.set_title('440Hz sine wave with peak amplitude 1.2')
    ax1.set_xlabel('Time (s)')
    ax1.set_xlim([0, 2048/44100])
    ax1.set_ylim([-1.6, 1.6])


    # plt.subplot(2, 1, 2)
    ax2.plot(ticks, clipped)#, '.-')
    ax2.set_title('Clipped at -1 and 1')
    ax2.set_xlabel('Time (s)')
    ax2.set_xlim([0, 2048/44100])
    ax2.set_ylim([-1.6, 1.6])

    plt.subplots_adjust(hspace=1)


    fig.savefig("../report/images/clipping.png")
    fig.show()

# clipping()

def hanning():
    ticks = np.arange(0.0, 2048/44100, 1/44100)
    hann = getHanningWindow(2048)

    fig, ax = plt.subplots()

    # plt.subplot(2, 1, 1)
    ax.plot(ticks, hann)#, 'o-')
    ax.set_title('Hanning Window with length 2048')
    ax.set_xlabel('Time (s)')
    ax.set_xlim([0, 2048/44100])

    fig.savefig("../report/images/hanning.png")
    plt.show()

# hanning()

def sectionCompression():
    pp = pickle.load(open("wavs/instrumentMelodies/CleanGuitar/CleanGuitarMelody6-4096.p", "rb"))
    data = pp.getIndexedPitchData()

    sections = data.copy()
    sections = pitchShift.compressIndexedPitchData2(sections)
    pitchShift.removeShortSections(sections, 8193)
    print(data, sections)
    print(len(data), len(sections))

    dataPred = [data[0][2]] + [x[2] for x in data]
    dataEnds = [0] + [x[1] for x in data]
    sectPred = [sections[0][2]] + [x[2] for x in sections]
    sectEnds = [0] + [x[1] for x in sections]

    dataX = [0]+np.arange(0, data[-1][0]+4096, 4096)
    sectX = np.arange(0, 212992, 4096)

    fig, (ax1, ax2) = plt.subplots(2,1)
    
    ax1.step(dataEnds, dataPred, where='pre')
    # ax1.plot(dataEnds, dataPred, 'x', color='black', alpha=1)
    ax1.set_ylabel('Frequency Prediction (Hz)')
    ax1.set_xlabel('Time (samples)')
    ax1.set_title('pitchData')
    ax1.set_xlim([0, 250000])
    ax1.set_ylim([0, 600])


    ax2.step(sectEnds, sectPred, where='pre')
    # ax2.plot(sectEnds, sectPred, 'x', color='black', alpha=1)
    ax2.set_ylabel('Frequency Prediction (Hz)')
    ax2.set_xlabel('Time (samples)')
    ax2.set_title('compressedPitchData')
    ax2.set_xlim([0, 250000])
    ax2.set_ylim([0, 600])

    fig.suptitle('Compression of indexedPitchData to \'sections\'')

    plt.subplots_adjust(hspace=0.4)

    fig.savefig("../report/images/sectionCompression.png")

    plt.show()

# sectionCompression()

def generatedSignalTypes():
    length = 500
    sine = signalGenerator.getSine(440, length, 44100)
    saw = signalGenerator.getSaw(440, length, 44100)
    square = signalGenerator.getSquare(440, length, 44100)
    triangle = signalGenerator.getTriangle(440, length, 44100)
    sineWithHarmonics = signalGenerator.getSineWithHarmonics(440, length, 44100, 10)

    time = np.arange(0.0, length/44100, 1/44100)

    lim = [0, length/44100]

    fig, (ax1, ax2, ax3, ax4, ax5) = plt.subplots(5, 1)

    fig.suptitle('Generated Signals')

    ax1.plot(time, sine)
    # ax1.set_ylabel('Magnitude')
    ax1.set_xlabel('Time (s)')
    ax1.set_title('Sine Wave')
    ax1.set_xlim(lim)

    ax2.plot(time, saw)
    # ax2.set_ylabel('Magnitude')
    ax2.set_xlabel('Time (s)')
    ax2.set_title('Saw Wave')
    ax2.set_xlim(lim)

    ax3.plot(time, square)
    # ax3.set_ylabel('Magnitude')
    ax3.set_xlabel('Time (s)')
    ax3.set_title('Square Wave')
    ax3.set_xlim(lim)

    ax4.plot(time, triangle)
    # ax4.set_ylabel('Magnitude')
    ax4.set_xlabel('Time (s)')
    ax4.set_title('Triangle Wave')
    ax4.set_xlim(lim)

    ax5.plot(time, sineWithHarmonics)
    # ax5.set_ylabel('Magnitude')
    ax5.set_xlabel('Time (s)')
    ax5.set_title('Sine Wave With 10 Harmonics')
    ax5.set_xlim(lim)

    plt.subplots_adjust(hspace=2)

    fig.savefig("../report/images/generatedSignalTypes.png")
    plt.show()

# generatedSignalTypes()