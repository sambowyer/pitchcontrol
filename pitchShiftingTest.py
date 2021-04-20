from testing import ratioTestToCSV, correctingTestToCSV, matchingTestToCSV
from PitchProfile import PitchProfile
import pickle, random
from helpers import getMajorScale, getMajorPentatonicScale

#Ratio Test
def ratioTest(numGeneratedSignalTests, numInstrumentTests, csvFile, testRecordFile, saveFolder=None, verbose=False):
    '''Run a desired number of ratio shifting tests on both generated signal melodies and instrument melodies. 
    NOTE: *testRecordFile* and *saveFolder* should already exist (if not equal to None), as should *csvFile* which should also already contain (at least) the header line.'''

    print("RATIO SHIFTING TEST")

    alreadyDone = [""]
    with open(testRecordFile, "r") as f:
        alreadyDone += [line.strip() for line in f.readlines()]

    print("Already done: %s" % (alreadyDone))

    #Generated Signal Test
    for testCount in range(numGeneratedSignalTests):
        testDetails = ""
        ratio = 1
        while testDetails in alreadyDone or ratio == 1:
            blockSize = [4096, 8192][random.randrange(2)]
            melodyNum = random.randrange(20)
            testFile = "wavs/generatedSignalMelodies/generatedSignalMelody%s-%s.p" % (melodyNum, blockSize)
            ratio = 2**((random.randrange(25) - 12)/12)
            testDetails = testFile+"SHIFTED"+str(ratio)

        alreadyDone.append(testDetails)

        with open(testRecordFile, "a") as f:
            f.write(testDetails + "\n")

        pp = pickle.load(open(testFile, "rb"))

        if saveFolder == None:
            ratioTestToCSV(pp, ratio, csvFile, verbose, None)
        else:
            ratioTestToCSV(pp, ratio, csvFile, verbose, saveFolder+"/"+testDetails.split("/")[-1][:-2]+".wav")

        print("%s/%s done. %s" % (testCount+1, numGeneratedSignalTests, testDetails))

    #Instrument Test
    instruments = ["LABSPiano",  "BBCCello", "BBCViolin", "BBCTrumpet", "BBCFlute", "CleanGuitar", "OverdriveGuitar"]
    for testCount in range(numInstrumentTests):
        testDetails = ""
        ratio = 1
        while testDetails in alreadyDone or ratio == 1:
            blockSize = [4096, 8192][random.randrange(2)]
            melodyNum = random.randrange(1,11)
            instrument = instruments[random.randrange(len(instruments))]
            testFile = "wavs/instrumentMelodies/%s/%sMelody%s-%s.p" % (instrument, instrument, melodyNum, blockSize)
            ratio = 2**((random.randrange(24) - 12)/12)
            testDetails = testFile+"SHIFTED"+str(ratio)

        alreadyDone.append(testDetails)

        with open(testRecordFile, "a") as f:
            f.write(testDetails + "\n")

        pp = pickle.load(open(testFile, "rb"))

        if saveFolder == None:
            ratioTestToCSV(pp, ratio, csvFile, verbose, None)
        else:
            ratioTestToCSV(pp, ratio, csvFile, verbose, saveFolder+"/"+testDetails.split("/")[-1][:-2]+".wav")

        print("%s/%s done. %s" % (testCount+1, numInstrumentTests, testDetails))

#Correcting Test
def correctingTest(numInstrumentTests, csvFile, testRecordFile, saveFolder=None, verbose=False):
    '''Run a desired number of pitch correcting tests on detuned instrument melodies. 
    Correction is done either to the chromatic scale, a major scale or a pentatonic major scale with repective probabilities 0.5, 0.25 and 0.25. In the case of major and major pentatonic scales the tonic note is chosen uniformly at random.
    NOTE: *testRecordFile* and *saveFolder* should already exist (if not equal to None), as should *csvFile* which should also already contain (at least) the header line.'''
    
    print("PITCH CORRECTION TEST")
    
    alreadyDone = [""]
    with open(testRecordFile, "r") as f:
        alreadyDone += [line.strip() for line in f.readlines()]

    print("Already done: %s" % (alreadyDone))

    #Instrument Test
    instruments = ["LABSPiano",  "BBCCello", "BBCViolin", "BBCTrumpet", "BBCFlute", "CleanGuitar", "OverdriveGuitar"]
    for testCount in range(numInstrumentTests):
        testDetails = ""
        while testDetails in alreadyDone:
            blockSize = [4096, 8192][random.randrange(2)]
            correctingToIndicator = random.random()
            if correctingToIndicator < 0.5:
                correctingTo = "chromatic"
                correctNotes = None
            else:
                correctingTo = ("C","C#","D","D#","E","F","F#","G","G#","A","A#","B")[random.randrange(12)]
                if correctingToIndicator < 0.75:
                    correctNotes = getMajorScale(correctingTo)
                    correctingTo += "major"
                else:
                    correctNotes = getMajorPentatonicScale(correctingTo)
                    correctingTo += "majorPentatonic"

            melodyNum = random.randrange(1,11)
            instrument = instruments[random.randrange(len(instruments))]
            testFile = "wavs/instrumentMelodies/Detuned/%s/%sMelody%sDETUNED-%s.p" % (instrument, instrument, melodyNum, blockSize)
            testDetails = testFile+"CORRECTED"+correctingTo

        alreadyDone.append(testDetails)

        with open(testRecordFile, "a") as f:
            f.write(testDetails + "\n")

        pp = pickle.load(open(testFile, "rb"))

        if saveFolder == None:
            correctingTestToCSV(pp, correctNotes, correctingTo, csvFile, verbose, None)
        else:
            correctingTestToCSV(pp, correctNotes, correctingTo, csvFile, verbose, saveFolder+"/"+testDetails.split("/")[-1][:-2]+".wav")

        print("%s/%s done. %s" % (testCount+1, numInstrumentTests, testDetails))

#Matching Test
def matchingTest(numCanvasTests, numNonCanvasTests, csvFile, testRecordFile, constBlockSize, saveFolder=None, verbose=False):
    '''Run a desired number of pitch matching tests with both canvas-to-melody and melody-to-melody matches.
    NOTE: *testRecordFile* and *saveFolder* should already exist (if not equal to None), as should *csvFile* which should also already contain (at least) the header line.'''
    
    print("PITCH MATCHING TEST")
    
    alreadyDone = [""]
    with open(testRecordFile, "r") as f:
        alreadyDone += [line.strip() for line in f.readlines()]

    print("Already done: %s" % (alreadyDone))

    #Canvas Tests
    instruments = ["LABSPiano",  "BBCCello", "BBCViolin", "BBCTrumpet", "BBCFlute", "CleanGuitar", "OverdriveGuitar", "generatedSignal"]
    canvasInstruments = ["LABSPiano",  "BBCCello", "BBCViolin", "BBCTrumpet", "BBCFlute", "CleanGuitar", "OverdriveGuitar", "sine", "saw", "square", "triangle", "sineWithHarmonics(20)"]
    for testCount in range(numCanvasTests):
        testDetails = ""
        while testDetails in alreadyDone:
            blockSize = [4096, 8192][random.randrange(2)]

            #Pick Canvas file
            canvasInstrument = canvasInstruments[random.randrange(len(canvasInstruments))]
            if canvasInstrument in ["sine", "saw", "square", "triangle", "sineWithHarmonics(20)"]:
                canvasFile = "wavs/generatedSignalMelodies/%sCanvas-%s.p" % (canvasInstrument, blockSize)
            else:
                canvasFile = "wavs/instrumentMelodies/%s/%sCanvas-%s.p" % (canvasInstrument, canvasInstrument, blockSize)


            if not constBlockSize:
                blockSize = [4096, 8192][random.randrange(2)]

            #Pick Melody file
            melodyInstrument = instruments[random.randrange(len(instruments))]
            if melodyInstrument == "generatedSignal":
                melodyFile = "wavs/generatedSignalMelodies/generatedSignalMelody%s-%s.p" % (random.randrange(20), blockSize)
            else:
                melodyFile = "wavs/instrumentMelodies/%s/%sMelody%s-%s.p" % (melodyInstrument, melodyInstrument, random.randrange(1,11), blockSize)

            testDetails = melodyFile+"MATCHED"+canvasFile

        alreadyDone.append(testDetails)

        with open(testRecordFile, "a") as f:
            f.write(testDetails + "\n")

        pp1 = pickle.load(open(canvasFile, "rb"))
        pp2 = pickle.load(open(melodyFile, "rb"))

        if saveFolder == None:
            matchingTestToCSV(pp1, pp2, csvFile, verbose, None)
        else:
            matchingTestToCSV(pp1, pp2, csvFile, verbose, saveFolder+"/"+melodyFile.split("/")[-1][:-2]+"MATCHED"+canvasFile.split("/")[-1][:-2]+".wav")

        print("%s/%s done. %s" % (testCount+1, numCanvasTests, testDetails))


    #Non-Canvas Tests (melody-to-melody pitch matching)
    for testCount in range(numNonCanvasTests):
        testDetails = ""
        while testDetails in alreadyDone:
            blockSize = [4096, 8192][random.randrange(2)]

            #Pick CanvasMelody file (not really a 'canvas' signal anymore but still useful to think of it as one)
            canvasMelodyInstrument = instruments[random.randrange(len(instruments))]
            if canvasMelodyInstrument == "generatedSignal":
                canvasMelodyFile = "wavs/generatedSignalMelodies/generatedSignalMelody%s-%s.p" % (random.randrange(20), blockSize)
            else:
                canvasMelodyFile = "wavs/instrumentMelodies/%s/%sMelody%s-%s.p" % (canvasMelodyInstrument, canvasMelodyInstrument, random.randrange(1,11), blockSize)


            if not constBlockSize:
                blockSize = [4096, 8192][random.randrange(2)]

            #Pick Melody file
            melodyInstrument = instruments[random.randrange(len(instruments))]
            if melodyInstrument == "generatedSignal":
                melodyFile = "wavs/generatedSignalMelodies/generatedSignalMelody%s-%s.p" % (random.randrange(20), blockSize)
            else:
                melodyFile = "wavs/instrumentMelodies/%s/%sMelody%s-%s.p" % (melodyInstrument, melodyInstrument, random.randrange(1,11), blockSize)

            testDetails = melodyFile+"MATCHED"+canvasMelodyFile

        alreadyDone.append(testDetails)

        with open(testRecordFile, "a") as f:
            f.write(testDetails + "\n")

        pp1 = pickle.load(open(canvasMelodyFile, "rb"))
        pp2 = pickle.load(open(melodyFile, "rb"))

        if saveFolder == None:
            matchingTestToCSV(pp1, pp2, csvFile, verbose, None)
        else:
            matchingTestToCSV(pp1, pp2, csvFile, verbose, saveFolder+"/"+melodyFile.split("/")[-1][:-2]+"MATCHED"+canvasMelodyFile.split("/")[-1][:-2]+".wav")

        print("%s/%s done. %s" % (testCount+1, numNonCanvasTests, testDetails))


# Now to quickly check that the tests work - both with and without saving the shifted audio files (this also allows us to check how the tests deal with stopping and starting)
def quickTestRun():
    ratioTest(1, 2, "csvs/ratioTest.csv", "testRecords/ratioTestRecord.txt", verbose=True)
    ratioTest(2, 1, "csvs/ratioTest.csv", "testRecords/ratioTestRecord.txt", "wavs/ratioTestOutputs", verbose=True)

    correctingTest(1, "csvs/correctingTest.csv", "testRecords/correctingTestRecord.txt")
    correctingTest(1, "csvs/correctingTest.csv", "testRecords/correctingTestRecord.txt", "wavs/correctingTestOutputs", verbose=True)

    matchingTest(1, 2, "csvs/matchingTest.csv", "testRecords/matchingTestRecord.txt", True, verbose=True)
    matchingTest(2, 1, "csvs/matchingTest.csv", "testRecords/matchingTestRecord.txt", False, verbose=True)
    matchingTest(1, 2, "csvs/matchingTest.csv", "testRecords/matchingTestRecord.txt", True, "wavs/matchingTestOutputs", verbose=True)
    matchingTest(2, 1, "csvs/matchingTest.csv", "testRecords/matchingTestRecord.txt", False, "wavs/matchingTestOutputs", verbose=True)

# quickTestRun()

# Now to run the actual tests to get all the data we want
# Note that since quickTestRun() was called twice before this we already have:
#   12 ratio tests (3 of generated signal melodies and 3 of instrument melodies)
#   4 correcting tests (all of (detuned) instrument melodies)
#   24 matching tests (12 matching with proper 'canvas' signals and 12 matching with non-'canvas' signals AND split half-and-half on the value of constBlockSize being True/False)
# so the test numbers in mainTest() result in us getting a total of 256 tests for each of the three types of test
# NOTE:
#       1. an error occured during the 56th generated signal ratioTest when mainTest() was first ran
#       2. an error occured during the 2nd generated signal ratioTest when mainTest() was ran for a second time on the test given by:
#               wavs/generatedSignalMelodies/generatedSignalMelody0-4096.pSHIFTED1.2599210498948732
#   Both errors occured when shifting the file generatedSignalMelody0.wav
#   1. Was fixed by changing the way min/maxExpectedBins were calculated in naiveFTWithPhase (and naiveFT for consistency)
#   2. Was fixed by including cases for frequencies being equal to 0 in getPercentageError, getAbsoluteMIDIError, isWithin100Cents, isWithin100CentsWithOctaveError
#   Strange behaviour that warrants more investigation but for now the tests can continue.
#   And hence why the first argument of the ratioTest call is 66 not 125
def mainTest():
    ratioTest(66, 125, "csvs/ratioTest.csv", "testRecords/ratioTestRecord.txt")

    correctingTest(252, "csvs/correctingTest.csv", "testRecords/correctingTestRecord.txt")

    matchingTest(48, 48, "csvs/matchingTest.csv", "testRecords/matchingTestRecord.txt", True)
    matchingTest(48, 48, "csvs/matchingTest.csv", "testRecords/matchingTestRecord.txt", False)

mainTest()