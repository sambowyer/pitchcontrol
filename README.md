# Pitch Control 
## CS Project 2020-21 (3rd Year 40-credit module)
### (A pitch detection and shifting program/library)

### Requirements (all available with pip)
- numpy
- soundfile
- midiutil (optional - only needed for [MIDIGenerator.py](MIDIGenerator.py) which has been used to prepare tests but is not really an important part of this project)

## Running pitchcontrol.py
Although much more functionality is possible using these python files more as a library (as was the case for the content of the report and the project as a whole), I have also written [pitchcontrol.py](pitchcontrol.py) as a simple command line interface for four of the basic use cases.

### Pitch Detection
Typing the following command will return the pitch predictions (and execution times) from all available pitch detection algorithms on the file 'signal.wav':
```
python3 pitchcontrol.py --detect signal.wav
```
`-d` may be used instead of `--detect`.

### Simple Pitch Shifting
The following command will perform a pitch shift of n semitones (where n must be an integer or a float) on the file 'signal.wav' and save the output in the file 'shifted.wav':
```
python3 pitchcontrol.py --shift signal.wav shifted.wav n
```
`-s` may be used instead of `--shift`.

### Pitch Correction
The following command will correct the frequencies of the notes inside 'signal.wav' (making sure they're all in tune) and save the output in the file 'corrected.wav':
```
python3 pitchcontrol.py --correct signal.wav corrected.wav
```
`-c` may be used instead of `--correct`.

### Pitch Matching
The following command will sequentially shift parts of 'original.wav' so that it matches the melody inside the file 'matching.wav' and save the output in the file 'matched.wav':
```
python3 pitchcontrol.py --match original.wav matching.wav matched.wav
```
`-m` may be used instead of `--match`.

(The 'simpler' the audio inside 'original.wav', the better the result is likely to be).


## Other Notable files
The file [signalGenerator.py](signalGenerator.py) can be used to generate the following common types of signals with a chosen frequency, length and sample rate:
- Sine wave
- Sawtooth wave
- Square wave
- Triangle wave
- Sine wave with *n* harmonics (where *n*is chosen by the user)

The file [helpers.py](helpers.py) also provides a wide range of features that may be useful for signal processing and frequency analysis.

The file [customFFT.py](customFFT.py) contains a simple forward fast fourier transform (FFT) implementation that may be used with any of the frequency-domain pitch detection algorithms (i.e. naiveFT, naiveFTWithPhase, cepstrum and HPS).