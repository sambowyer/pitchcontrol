import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from helpers import getMidiNoteWithCents
#metrics to check:
#   (0) % error (based on Hz values)
#   (1) absolute error in midiValue - since musical notes are distributed on Hz logarithmically this may make more sense than (1)
#   (2) % of predictions within 100 cents of true frequency
#   (3) % of predictions within 100 cents of true frequency +\- 1 octave

# (0)
def getPercentageError(expectedFreq, actualFreq):
    return (abs(expectedFreq-actualFreq))/expectedFreq

#(1)
def getPercentageMIDIError(expectedFreq, actualFreq):
    return abs(getMidiNoteWithCents(expectedFreq) - getMidiNoteWithCents(actualFreq))

#(2)
def isWithin100Cents(expectedFreq, actualFreq):
    return int(abs(getMidiNoteWithCents(expectedFreq) - getMidiNoteWithCents(actualFreq)) <= 0.5)

#(3)
def isWithin100CentsWithOctaveError(expectedFreq, actualFreq):
    diff = abs(getMidiNoteWithCents(expectedFreq) - getMidiNoteWithCents(actualFreq))
    return int(diff <= 0.5 or (diff <= 12.5 and diff >= 11.5))


def getMeanTimeAndErrors(conditions, csvFilePath, verbose=False):
    '''Returns a list of the form [mean time, mean percentErr, mean absMidiErr, mean correctNote, mean correctNoteWithOctaveErr] 
    where the mean values are taken across csv lines in *csvFilePath* that meet the conditions given in the dictionary *conditions*
        e.g. the conditions dictionary {isCustomFFT : [True]} will average out results of all test cases where isCustomFFT=True
        whereas the dictionary {isCustomFFT : [True, False]} will average out results of all test cases where isCustomFFT=True OR isCustomFFT=False'''
    meanTimeAndErrors = [0,0,0,0,0]
    count = 0

    with open(csvFilePath,"r") as f:
        headers = f.readline().strip().replace(" ","").split(",")
        
        conditionIndices = []
        for condtionVar in conditions:
            headerIndex = 0
            for header in headers:
                if condtionVar == header:
                    conditionIndices.append(headerIndex)
                    break
                headerIndex += 1

        line = f.readline()
        while line:
            line = line.strip().replace(" ","").split(",")

            meetsConditions = True
            conditionIndex = 0
            for condition in conditions:
                if line[conditionIndices[conditionIndex]] not in conditions[condition]:
                    meetsConditions = False
                    break
                conditionIndex += 1

            if meetsConditions:
                count += 1
                for i in range(5):
                    meanTimeAndErrors[i] += float(line[-(5-i)])

            line = f.readline()
            line1 = False
        
    if count == 0:
        if verbose:
            print("No lines found to match condition %s" % (conditions))
        return [-1,-1,-1,-1,-1]
    
    meanTimeAndErrors = [x/count for x in meanTimeAndErrors]

    if verbose:
        print("Mean Time: %ss\nMean Percent Error (Hz): %s\nMean Absolute MIDI Error: %s\nProportion correct (+/- 50 cents): %s\nProportion correct (+/- 50 cents) w/ octave error: %s" % (meanTimeAndErrors[0],meanTimeAndErrors[1],meanTimeAndErrors[2],meanTimeAndErrors[3],meanTimeAndErrors[4]))

    return meanTimeAndErrors

def printOptimisationTestAnalysis():
    print("Optimising 'b' (in AMDF)")
    print("b=0.5")
    getMeanTimeAndErrors({"b" : ["0.5"], "algorithm" : ["AMDF"]}, "csvs/optimisationTest.csv", True)
    print("b=1")
    getMeanTimeAndErrors({"b" : ["1"], "algorithm" : ["AMDF"]}, "csvs/optimisationTest.csv", True)
    print("b=2")
    getMeanTimeAndErrors({"b" : ["2"], "algorithm" : ["AMDF"]}, "csvs/optimisationTest.csv", True)
    print()

    print("Optimising 'isCustomFFT'")
    print("isCustomFFT=False")
    getMeanTimeAndErrors({"isCustomFFT" : ["False"], "algorithm" : ["naiveFT", "naiveFTWithPhase", "cepstrum", "HPS"]}, "csvs/optimisationTest.csv", True)
    print("isCustomFFT=True")
    getMeanTimeAndErrors({"isCustomFFT" : ["True"], "algorithm" : ["naiveFT", "naiveFTWithPhase", "cepstrum", "HPS"]}, "csvs/optimisationTest.csv", True)
    print()

    print("Optimising 'numDownsamples' (in HPS)")
    print("numDownsamples=2")
    getMeanTimeAndErrors({"numDownsamples" : ["2"], "algorithm" : ["HPS"]}, "csvs/optimisationTest.csv", True)
    print("numDownsamples=4")
    getMeanTimeAndErrors({"numDownsamples" : ["4"], "algorithm" : ["HPS"]}, "csvs/optimisationTest.csv", True)
    print("numDownsamples=6")
    getMeanTimeAndErrors({"numDownsamples" : ["6"], "algorithm" : ["HPS"]}, "csvs/optimisationTest.csv", True)
    print()

    print("Optimising 'octaveTrick'")
    print("octaveTrick=False")
    getMeanTimeAndErrors({"octaveTrick" : ["False"], "algorithm" : ["HPS"]}, "csvs/optimisationTest.csv", True)
    print("octaveTrick=True")
    getMeanTimeAndErrors({"octaveTrick" : ["True"], "algorithm" : ["HPS"]}, "csvs/optimisationTest.csv", True)
    print()

    print("Optimising sampleRate (for generated signals)")
    print("sampleRate=22050")
    getMeanTimeAndErrors({"sampleRate" : ["22050"], "instrument" : ["n/a"]}, "csvs/optimisationTest.csv", True)
    print("sampleRate=441000")
    getMeanTimeAndErrors({"sampleRate" : ["44100"], "instrument" : ["n/a"]}, "csvs/optimisationTest.csv", True)
    print()


printOptimisationTestAnalysis()

## For use with old csv format (i.e. generatedSignalsTest.csv and wavTests.csv)
# separate results based firstly by algorithm and secondly by type of wave
def getDictionaryOfErrors(csvFilePath):
    '''returns a dictionary of the form:
            keys   - algorithm name ('zerocross', 'autocorrelation', etc.)
            values - dictionaries of the form:
                keys   - signal name ('sine', 'saw', etc.)
                values - array containing one sub-array for each instance of this particular algorithm-signalType test in csvFilePath:
                    each sub-array of length 4 with each element corresponding to the following 4 error-values:
                        (0) % error (based on Hz values)
                        (1) absolute error of midi values
                        (2) % of predictions within 100 cents of true frequency
                        (3) % of predictions within 100 cents of true frequency +\- 1 octave
    '''
    dictionary = {}
    with open(csvFilePath, "r") as f:
        for line in f:
            if line != "signalType,sampleRate,algorithm,algorithmParameters,trueFreq,predFreq,time\n":
                data = line.rstrip().split(",")

                if data[2] not in dictionary:
                    dictionary[data[2]] = {}
                
                if data[0] not in dictionary[data[2]]:
                    dictionary[data[2]][data[0]] = []

                expectedFreq = float(data[4])
                actualFreq = float(data[5])

                errors = [getPercentageError(expectedFreq,actualFreq), getPercentageMIDIError(expectedFreq, actualFreq), isWithin100Cents(expectedFreq, actualFreq), isWithin100CentsWithOctaveError(expectedFreq, actualFreq)]

                dictionary[data[2]][data[0]].append(errors)


    return dictionary
            
def getDictionaryOfAverageErrors(dictionaryOfErrors):
    '''returns a dictionary of the form:
            keys   - algorithm name ('zerocross', 'autocorrelation', etc.)
            values - dictionaries of the form:
                keys   - signal name ('sine', 'saw', etc.)
                values - array of length 4 with each element corresponding to average amongst errors in dictionaryOfErrors for the following 4 error-values:
                        (0) % error (based on Hz values)
                        (1) absolute error of midi values
                        (2) % of predictions within 100 cents of true frequency
                        (3) % of predictions within 100 cents of true frequency +\- 1 octave
    '''
    dictionary = {}
    for algorithm in dictionaryOfErrors:

        if algorithm not in dictionary:
            dictionary[algorithm] = {}

        for signalType in dictionaryOfErrors[algorithm]:
            
            if signalType not in dictionary:
                dictionary[algorithm][signalType] = [0,0,0,0]

            for i in range(4):
                errors = [testCase[i] for testCase in dictionaryOfErrors[algorithm][signalType]]
                dictionary[algorithm][signalType][i] = sum(errors)/len(errors)

    return dictionary

def printDictionaryOfAverageErrors(avgErrDict):         
    for algorithm in avgErrDict:
        print(algorithm)
        for signal in avgErrDict[algorithm]:
            print(signal, end=": ")
            print(avgErrDict[algorithm][signal])
        print()

###### REDO OR DISCOUNT THIS FUNCTION FROM FINAL GIT COMMIT B/C HEAVILY RELIES ON TUTORIAL @ 
###### https://matplotlib.org/stable/gallery/lines_bars_and_markers/barchart.html#sphx-glr-gallery-lines-bars-and-markers-barchart-py
def showErrorGraphs(avgErrDict, errorType, signalTypes):
    labels = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "cepstrum", "HPS", "median"] #ignoring the 'average' label for now
    signalErrors = []
    for signalType in signalTypes:
        signalErrors.append([avgErrDict[algorithm][signalType][errorType] for algorithm in labels])

    # sineErrors = [avgErrDict[algorithm]["sine"][errorType] for algorithm in labels]
    # sawErrors = [avgErrDict[algorithm]["saw"][errorType] for algorithm in labels]
    # squareErrors = [avgErrDict[algorithm]["square"][errorType] for algorithm in labels]
    # triangleErrors = [avgErrDict[algorithm]["triangle"][errorType] for algorithm in labels]
    # sineWith10HarmonicsErrors = [avgErrDict[algorithm]["sineWith10Harmonics"][errorType] for algorithm in labels]
    # sineWith20HarmonicsErrors = [avgErrDict[algorithm]["sineWith20Harmonics"][errorType] for algorithm in labels]

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()

    rectsList = []
    for i, signalType in enumerate(signalTypes):
        rectsList.append(ax.bar(x - (1-len(signalTypes)+2*i)*width/len(signalTypes), signalErrors[i], width/3, label=signalType))

    # rects1 = ax.bar(x - 5*width/6, sineErrors, width/3, label='sine')
    # rects2 = ax.bar(x - 3*width/6, sawErrors, width/3, label='saw')
    # rects3 = ax.bar(x - width/6, squareErrors, width/3, label='square')
    # rects4 = ax.bar(x + width/6, triangleErrors, width/3, label='triangle')
    # rects5 = ax.bar(x + 3*width/6, sineWith10HarmonicsErrors, width/3, label='sine with 10 harmonics')
    # rects6 = ax.bar(x + 5*width/6, sineWith20HarmonicsErrors, width/3, label='sine with 20 harmonics')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    if errorType == 0:
        ax.set_ylabel('Mean Percentage Error')
        ax.set_title('Mean percentage errors of predictions in Hz\n(by pitch detection algorithm and signal type)')
    if errorType == 1:
        ax.set_ylabel('Mean Absolute Error')
        ax.set_title('Mean absolute error of MIDI note prediction\n(by pitch detection algorithm and signal type)')
    if errorType == 2:
        ax.set_ylabel('Proportion')
        ax.set_title('Proportion of predictions correct to nearest note\n(by pitch detection algorithm and signal type)')
    if errorType == 3:
        ax.set_ylabel('Proportion')
        ax.set_title('Proportion of predictions correct to nearest note +/- one octave\n(by pitch detection algorithm and signal type)')

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    # def autolabel(rects):
    #     """Attach a text label above each bar in *rects*, displaying its height."""
    #     for rect in rects:
    #         height = rect.get_height()
    #         ax.annotate('{}'.format(height),
    #                 xy=(rect.get_x() + rect.get_width() / 2, height),
    #                 xytext=(0, 3),  # 3 points vertical offset
    #                 textcoords="offset points",
    #                 ha='center', va='bottom')

    # autolabel(rects1)
    # autolabel(rects2)
    # autolabel(rects3)
    # autolabel(rects4)
    # autolabel(rects5)
    # autolabel(rects6)

    fig.tight_layout()

    plt.show()

def analyseGeneratedSignalsTest():
    avgErrDict = getDictionaryOfAverageErrors(getDictionaryOfErrors("csvs/generatedSignalsTest.csv"))
    printDictionaryOfAverageErrors(avgErrDict)
    for i in range(4):
        showErrorGraphs(avgErrDict, i, ["sine", "saw", "square", "triangle", "sineWith10Harmonics", "sineWith20Harmonics"])

def analyseWavTests():
    avgErrDict = getDictionaryOfAverageErrors(getDictionaryOfErrors("csvs/wavTests.csv"))
    for i in range(4):
        showErrorGraphs(avgErrDict, i, ["guitarC3", "trebleVoiceA4"])