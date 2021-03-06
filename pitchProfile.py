from predict import zerocross, autocorrelation, AMDF, naiveFT, naiveFTWithPhase, cepstrum, HPS
from helpers import midiToFreq, getMidiNoteWithCents, getPitchInfo, getTrimmedMean, toMono
from timeit import default_timer as timer
import soundfile as sf

#dictionary containing typical ranges offundamental frequencies for a variety of instruments
#note that these ranges are all padded on either side by 250 cents to allow for the inescapable error that all of the pitch detection algorithms have built-in
#(particularly for those algorithms involving frequency (or quefrency) bins)
#actual ranges are as follows (rounded to 2dp, both guitar and bass guitar assume 24 frets and voice is for someone who can sing as a bass all the way to a soprano): 
#       piano       - A0-C8  =  27.50 Hz - 4186.01 Hz         -/+250cents =  23.80 Hz - 4836.32 Hz
#       guitar      - E2-E6  =  82.41 Hz - 1318.51 Hz         -/+250cents =  71.33 Hz - 1523.34 Hz
#       cello       - C2-A5  =  65.41 Hz -  880.00 Hz         -/+250cents =  56.61 Hz - 1016.71 Hz
#       violin      - G3-A7  = 196.00 Hz - 3520.00 Hz         -/+250cents = 169.64 Hz - 4066.84 Hz
#       voice       - F2-C6  =  87.31 Hz - 1046.50 Hz         -/+250cents =  75.57 Hz - 1209.08 Hz
#       bass guitar - E1-E5  =  41.20 Hz -  659.26 Hz         -/+250cents =  35.66 Hz -  761.67 Hz
#       trumpet     - F#3-D6 = 185.00 Hz - 1174.66 Hz         -/+250cents = 160.12 Hz - 1357.15 Hz
#       flute       - C4-C7  = 261.63 Hz - 2093.00 Hz         -/+250cents = 226.45 Hz - 2418.16 Hz
instrumentRanges = {"piano" : [23.8,4836.32], "guitar" : [71.33,1523.34], "cello" : [56.51,1016.71], "violin" : [169.64,4066.84], "voice" : [75.57,1209.08], "bass guitar" : [35.66,761.67], "trumpet":[160.12,1357.15], "flute":[226.45,2418.16]}

class PitchProfile:
    def __init__(self, location, sampleRate, detectionMode, detectionParams, instrument=None, blockSize=2048, overlap=1024, windowFunction=None, customName=None):
        self.location = location #location of the file corresponding to this pitchProfile object

        self.sampleRate = sampleRate #sampleRate of the signal

        self.detectionMode = detectionMode #pitch detectino algorithm to use in analysing the pitch of the signal
        self.detectionParams = detectionParams #dictionary containing relevant parameters for whichever pitch detection algorithm is being used

        self.instrument = instrument
        self.setExpectedFrequencyRange(instrument=self.instrument)

        self.blockSize = blockSize #size of chunks by which the signal is split up into and pitch is found individually for
        self.overlap = overlap #amount by which chunks overlap
        self.windowFunction = windowFunction
        if self.windowFunction == None:
            self.windowFunction = [1 for i in range(self.blockSize)] # defaults to a rectangular window

        if customName == None:
            self.name = location.split("/")[-1]
        else:
            self.name = customName

        self.pitchData = []

        self.analysisTime = 0

    def setExpectedFrequencyRange(self, minimum=20, maximum=20000, instrument=None):
        '''Changes the values corresponding to the keys "expectedMin" & "expectedMax" within the dictionary *detectionParams*
        If instrument is given as a string with the name of an instrument this function will attempt to set the min/max accordingly'''
        if instrument == None:
            self.detectionParams["expectedMin"] = minimum
            self.detectionParams["expectedMax"] = maximum
        elif instrument in instrumentRanges:
            self.detectionParams["expectedMin"] = instrumentRanges[instrument][0]
            self.detectionParams["expectedMax"] = instrumentRanges[instrument][1]
            

    def getLog(self):
        '''Returns out a log summarising the pitchProfile object.'''
        log = "Pitch Profile Log for \'%s\'\nLocation: %s\nPitch Detection Algorithm: %s\n    params: %s\nSample rate: %s\nBlock size: %s\n" % (self.name, self.location, self.detectionMode, self.detectionParams, self.sampleRate, self.blockSize)
        if self.instrument != None:
            log += "Instrument: %s\n\n" % (self.instrument)
        log += "PITCH ANALYSIS (took %ss) - Average Pitch = %sHz\n" % (self.analysisTime, getTrimmedMean(self.pitchData, 0.4))

        frameCount = 0
        for prediction in self.pitchData:
            log += "%s-%s: %s\n" % (frameCount, frameCount+self.blockSize, getPitchInfo(prediction))
            frameCount += self.blockSize - self.overlap

        return log

    def printLog(self):
        print(self.getLog())

    def writeLog(self, writeLocation):
        with open(writeLocation, "w") as f:
            f.write(self.getLog())

    def getIndexedPitchData(self):
        '''Returns list of sublists of the form
                [blockStartIndex, blockEndIndex, pitchPrediction]
            for each block in self.pitchData, where:
                blockStartIndex = index within the whole signal that the block begins at
                blockEndIndex   = index within the whole signal that the block ends at
                pitchPrediction = pitch prediction (in Hz) for this block'''
        return [[i*(self.blockSize-self.overlap), i*(self.blockSize-self.overlap)+self.blockSize, self.pitchData[i]] for i in range(len(self.pitchData))]

    def autoCorrectPitchData(self, correctNotes=None):
        '''If correctNotes=None this corrects the frequency values in self.pitchData to be exactly in tune (by the A440 equal temperament tuning standard).
        If instead correctNotes is an array of the midi values that are 'acceptable' then the frequency values in self.pitchData are tweaked so that they are equal to the frequency of the 'acceptable' midi note that each original pitchData frequency is clsoest to.'''
        if correctNotes == None:
            for i in range(len(self.pitchData)):
                self.pitchData[i] = midiToFreq(round(getMidiNoteWithCents(self.pitchData[i])))
        else:
            for i in range(len(self.pitchData)):
                midiValue = getMidiNoteWithCents(self.pitchData[i])

                closestCorrectValue = correctNotes[0]
                midiError = abs(closestCorrectValue-midiValue)
                for note in correctNotes[1:]:
                    if abs(note-midiValue) < midiError:
                        midiError = abs(note-midiValue)
                        closestCorrectValue = note

                self.pitchData[i] = midiToFreq(closestCorrectValue)

    def predictPitch(self, partialSignal):
        if self.detectionMode == "zerocross":
            return zerocross(partialSignal, self.sampleRate)
        elif self.detectionMode == "autocorrelation":
            return autocorrelation(partialSignal, self.sampleRate, self.detectionParams["expectedMin"], self.detectionParams["expectedMax"])
        elif self.detectionMode == "AMDF":
            return AMDF(partialSignal, self.sampleRate, self.detectionParams["b"], self.detectionParams["expectedMin"], self.detectionParams["expectedMax"])
        elif self.detectionMode == "naiveFT":
            return naiveFT(partialSignal, self.sampleRate, self.detectionParams["isCustomFFT"], self.detectionParams["expectedMin"], self.detectionParams["expectedMax"])
        elif self.detectionMode == "naiveFTWithPhase":
            return naiveFTWithPhase(partialSignal, self.sampleRate, self.detectionParams["isCustomFFT"], self.detectionParams["expectedMin"], self.detectionParams["expectedMax"])
        elif self.detectionMode == "cepstrum":
            return cepstrum(partialSignal, self.sampleRate, self.detectionParams["isCustomFFT"], self.detectionParams["expectedMin"], self.detectionParams["expectedMax"])
        elif self.detectionMode == "HPS":
            return HPS(partialSignal, self.sampleRate, self.detectionParams["isCustomFFT"], self.detectionParams["numDownsamples"], self.detectionParams["expectedMin"], self.detectionParams["expectedMax"])
        else:
            print("ERROR") #CHANGE THIS SO IT ACTUALLY THROWS AN ERROR


    def analysePitch(self):
        '''returns a list of pitch predictions for each block in this object's signal.'''
        start = timer()
        if sf.info(self.location).channels > 1:
            partialSignals = [toMono(sig) for sig in sf.blocks(self.location, blocksize=self.blockSize, overlap=self.overlap)]
        else:
            partialSignals = sf.blocks(self.location, blocksize=self.blockSize, overlap=self.overlap)

        pitchData = []
        for sig in partialSignals:
            # print(len(sig))
            prediction = self.predictPitch([sig[i]*self.windowFunction[i] for i in range(len(sig))])
            if prediction == 0:
                prediction = 2.2250738585072014e-308
            pitchData.append(prediction)

        end = timer()

        self.pitchData = pitchData
        self.analysisTime = end-start

    def getSignal(self):
        return sf.read(self.location)[0] 