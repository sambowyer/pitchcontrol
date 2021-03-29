import testing
from helpers import toMono
import soundfile as sf

signal, sampleRate = sf.read('wavs/guitarC3.wav')
testing.testAllAlgorithmsToCSV(toMono(signal[1000:3048]), sampleRate, "guitarC3", 440*(2**((1/12) * -21)), "csvs/wavTests.csv")

signal, sampleRate = sf.read('wavs/trebleVoiceA4.wav')
testing.testAllAlgorithmsToCSV(toMono(signal[1000:3048]), sampleRate, "trebleVoiceA4", 440, "csvs/wavTests.csv")