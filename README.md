# Pitch Control 
## CS Project 2020-21 (3rd Year 40-credit module)
### (A pitch detection and shifting program/library)

A command-line program providing a range of pitch detection algorithms with pitch shifting capability. Although the project can be thought of as a library, a command -ine interface is available (using [pitchControl.py](pitchControl.py)) for some of the more important use cases.

### Requirements (all available with pip)
- numpy
- soundfile
- midiutil (optional - only needed for [MIDIGenerator.py](MIDIGenerator.py) which has been used to prepare tests but is not really an important part of this project)


## Pitch Detection
There are six different pitch detection algorithms avaiable to use (all located in [predict.py](predict.py)):
- **zerocross**
  - Calculates the average distance (in samples) between points where the signal changes between positive and negative values, then assumes that this is half the signal's period and uses the sample rate information to make a frequency prediction.
  - [ADD CODE/CMD]
- **autocorrelation**
  - Predicts the frequency of a mono signal by finding the time interval (of m samples) for which the signal most consistently repeats itself. Autocorrelation uses the product of signal values at intervals of m samples to find this optimal m.
  - [ADD CODE/CMD]
- **AMDF** (Average Magnitude Differential Function)
  - Predicts the frequency of a mono signal by finding the time interval (of m samples) for which the signal most consistently repeats itself. AMDF uses the Euclidean distance (to the power of b) between signal values at intervals of m samples to find this optimal m.
  - [ADD CODE/CMD]
- **naiveFT**
  - Predicts the frequency of a mono signal simply by picking the largest peak in the  Fourier-transform of the signal.
  - [ADD CODE/CMD]
- **Cepstrum**
  - Predicts the frequency of a mono signal by finding the period which most strongly correlates to the distance between peaks in the Fourier-transform of the signal.
    Assuming the peaks in the Fourier transform are located at harmonics of the signal, this period should represent the distance between the harmonics, i.e. the fundamental period.
    [ADD CODE/CMD]
- **HPS** (Harmonic Product Spectrum)
  - Predicts the frequency of a mono signal by first computing (the magnitudes within) its Fourier-transform and then resampling (downsampling) this by factors of 1/2, 1/3, 1/4, etc. . Then we may multiply these downsampled versions and can expect a peak correlating to the fundamental frequency of the original signal.
  - [ADD CODE/CMD]

The option to get the mean prediction among all six algorithms is also available with the function *getTrimmedMeanPrediction*.

[pitchProfile.py](pitchProfile.py) also defines a *PitchProfile* object which analyses .wav files and provides information about the file's pitch over time (using one of the six aforementioned pitch detection algorithms).

## Pitch Shifting
A standard phase vocoder is implemented in [pitchShift.py](pitchShift.py)), allowing users to stretch or compress a signal without affecting the frequency.
- [ADD CODE/CMD]
  
Once a signal has been stretched/compressed by the phase vocoder, we may resample the result at an altered sample rate to obtain a pitch-shifted version of the original signal (hopefully with minimal glitches - though some signals do fare better than others). The following pitch shifting features are available to use (located in [pitchShift.py](pitchShift.py)):
- Pitch shifting **by ratio**
  - [ADD CODE/CMD]
- Pitch **correction**
  - [ADD CODE/CMD]
- Pitch **matching**
  - [ADD CODE/CMD]

## Miscellaneous
The file [signalGenerator.py](signalGenerator.py) can be used to generate the following common types of signals with a chosen frequency, length and sample rate:
- Sine wave
- Sawtooth wave
- Square wave
- Triangle wave
- Sine wave with *n* harmonics (where *n*is chosen by the user)

The file [helpers.py](helpers.py) also provides a wide range of features that may be useful for signal processing and frequency analysis (as well as a simple short time fourier transform (STFT)).

The file [customFFT.py](customFFT.py) contains a simple forward fast fourier transform (FFT) implementation that may be used with any of the time-domain pitch detection algorithms (i.e. naiveFT, cepstrum and HPS).