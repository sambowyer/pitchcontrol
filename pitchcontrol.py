import sys, getopt, math, logging, argparse
from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS
from helpers import *
import signalGenerator
import numpy as np
from timeit import default_timer as timer
import soundfile as sf

shortArgs = "hvg:da:b:cn:pr:sm:f:i:o:"
longArgs = ["help", "verbose", "generate=", "detect", "algorithm=", "b=", "customFFT", "numDownsamples=", "profile", "range=", "shift", "mode=", "factor=", "input=","output="]
# hyperparameters added on end of command

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:],shortArgs,longArgs)
    except getopt.GetoptError:
        print('pitchcontrol.py -i <inputfile> -o <outputfile>')
        sys.exit(2)

    print(opts, args)
    verbose = False
    inputFile = ""
    outputFile = ""
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print('''pitchcontrol.py usage

A command-line tool for signal generating, pitch detection and pitch shifting.

        (python[3]) pitchcontrol [-abcdghimnoprstv] [output file]

-a  --algorithm         Algorithm to use in pitch detection. Must be one of 'zerocross', 'autocorrelation', 'AMDF', 'naiveFT', 'cepstrum', 'HPS' or 'median' - default='zerocross'.
-b  --b                 Hyperparameter for exponent in AMDF calculation. Default value is 1.
-c  --customFFT         Select if you want to use a custom FFT implementation in pitch detection rather than the default numpy implementation.
-d  --detect            Select if you want to use the pitch detection features rather than signal generating or pith shifting.
-g  --generate          Must be followed by:
                            - signal type (one of sine/saw/square/triangle/sine[num] - if [num] is provided (as an integer) this will generate a sine wave with [num] harmonics.
                        Optional arguments may also be provided (in this order):
                            - frequency (Hz)    - default = 440
                            - length (samples)  - default = 44100
                            - sample rate (Hz)  - default = 44100
-h  --help              Print this usage information to output.
-i  --input             File for pitch detection or pitch shifting.
-m  --mode              Mode of pitch shifting. Must be one of the following:
                            - 'ratio'   - must be followed by a ratio to pitch shift the input file by.
                            - 'correct' - attempts to correct the pitches of the input file so that they are all in tune.
                            - 'match'   - must be followed by a file whose pitch-over-time profile will be used to retune the input file.
-n  --numDownSamples    Hyperparameter for HPS calculation.
-o  --output            Filename for the output of signal generating, pitch shifting or pitch profile log.
-p  --profile           Select if you want to create (and then save as a .pkl along with a corresponding log file with name specified by -o/--output) a pitch profile of the input file.
-r  --range             Range of expected frequencies in pitch detection. Either write in the form 'x-y' where x and y are numerical upper and lower bounds in Hz, or select from one of 'piano', 'guitar', 'cello', 'violin', 'voice', 'bass-guitar', 'trumpet' or 'flute'.
-s  --shift             Select if you want to use the pitch shifting features rather than signal generating or pith detection.
-v  --verbose           Select if you want text output as operations are processing.

Examples:
1. Create a sine wave with 10 harmonics of frequency 220Hz, length 1000 samples and sample rate 22050Hz and save to 'sine220.wav':
        (python[3]) pitchcontrol.py -g sine10 220 1000 22050 -o sine220.wav
        (python[3]) pitchcontrol.py --generate sine10 220 1000 22050 --output sine220.wav

2. Detect the pitch of a file 'audio.wav' using AMDF with b=1.5 and the expected frequency range of a trumpet:
        (python[3]) pitchcontrol.py -d -a AMDF -b 1.5 -r trumpet -i audio.wav
        (python[3]) pitchcontrol.py --detect --algorithm AMDF --b 1.5 --range trumpet --input audio.wav

3. Write out a pitch profile of a file 'audio.wav' using naiveFT and customFFT to 'audioprofile.log' (the PitchProfile pbject will be written to 'audioprofile.pkl'):
        (python[3]) pitchcontrol.py -p -a cepstrum -c -o audioprofile.log
        (python[3]) pitchcontrol.py --profile --algorithm cepstrum --customFFT --output audioprofile.log

4. Match the pitch of the PitchProfile stored in 'match.pkl' using the source sound file 'audio.wav' and output it to 'matchedAudio.wav':
        (python[3]) pitchcontrol.py -s -m match match.pkl -i audio.wav -o  matchedAudio.wav
        (python[3]) pitchcontrol.py --shift --mode match match.pkl --input audio.wav --output matchedAudio.wav


N.B.:   Input files may either be .wav or .pkl if the .pkl file is storing a PitchProfile object with its corresponding .wav file still in its original location.
        Outfile sound files must be in .wav format. If this file extension is not entered it will be assumed.
        
''')
        if opt in ("-v","--verbose"):
            verbose = True
        else:
            print("B")
        # logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    # data, samplerate = sf.read(file)




if __name__ == "__main__":
    # parser = argparse.ArgumentParser()
    # parser.add_argument("-v", "--verbose", action="store_true")

    # parser.add_argument("-g", "--generate", action="store_true", help="Generate a signal of type 'sine'/'saw'/'square'/'triangle' with given frequency (Hz), length (samples), and sample rate (Hz) and save to output file.")

    # parser.add_argument("-d", "--detect", action="store_true", help="Generate a signal of type 'sine'/'saw'/'square'/'triangle' with given frequency (Hz), length (samples), and sample rate (Hz) and save to output file.")


    # args = parser.parse_args()




    main()