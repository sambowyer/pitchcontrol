
import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from pitchcontrol import getMidiNoteWithCents
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
    labels = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "cepstrum", "HPS"]
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

avgErrDict = getDictionaryOfAverageErrors(getDictionaryOfErrors("csvs/generatedSignalsTest.csv"))
for i in range(4):
    showErrorGraphs(avgErrDict, i, ["sine", "saw", "square", "triangle", "sineWith10Harmonics", "sineWith20Harmonics"])

avgErrDict = getDictionaryOfAverageErrors(getDictionaryOfErrors("csvs/wavTests.csv"))
for i in range(4):
    showErrorGraphs(avgErrDict, i, ["guitarC3", "trebleVoiceA4"])