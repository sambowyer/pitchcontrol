import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from helpers import getMidiNoteWithCents

## GENERAL ANALYSIS FUNCTIONS

#metrics to check:
#   (0) % error (based on Hz values)
#   (1) absolute error in midiValue - since musical notes are distributed on Hz logarithmically this may make more sense than (1)
#   (2) % of predictions within 100 cents of true frequency
#   (3) % of predictions within 100 cents of true frequency +\- 1 octave

# (0)
def getPercentageError(expectedFreq, actualFreq):
    return (abs(expectedFreq-actualFreq))/expectedFreq

#(1)
def getAbsoluteMIDIError(expectedFreq, actualFreq):
    return abs(getMidiNoteWithCents(expectedFreq) - getMidiNoteWithCents(actualFreq))

#(2)
def isWithin100Cents(expectedFreq, actualFreq):
    return int(abs(getMidiNoteWithCents(expectedFreq) - getMidiNoteWithCents(actualFreq)) <= 0.5)

#(3)
def isWithin100CentsWithOctaveError(expectedFreq, actualFreq):
    diff = abs(getMidiNoteWithCents(expectedFreq) - getMidiNoteWithCents(actualFreq))
    return int(diff <= 0.5 or (diff <= 12.5 and diff >= 11.5))

def getMeanTimeAndErrors(conditions, csvFilePath, verbose=False, freqRange = [20,20000], partialConditions=None, partialAtStart=True):
    '''Returns a list of the form [mean time, mean percentErr, mean absMidiErr, mean correctNote, mean correctNoteWithOctaveErr] 
    where the mean values are taken across csv lines in *csvFilePath* that meet the conditions given in the dictionary *conditions*
        e.g. the conditions dictionary {isCustomFFT : [True]} will average out results of all test cases where isCustomFFT=True
        whereas the dictionary {isCustomFFT : [True, False]} will average out results of all test cases where isCustomFFT=True OR isCustomFFT=False'''
    meanTimeAndErrors = [0,0,0,0,0]
    count = 0

    with open(csvFilePath,"r") as f:
        headers = f.readline().strip().replace(" ","").split(",")
        
        conditionIndices = []
        trueFreqIndex = 13

        for condtionVar in conditions:
            headerIndex = 0
            for header in headers:
                if condtionVar == header:
                    conditionIndices.append(headerIndex)
                    break
                headerIndex += 1

        partialConditionIndices = []

        if partialConditions != None:
            for condtionVar in partialConditions:
                headerIndex = 0
                for header in headers:
                    if condtionVar == header:
                        partialConditionIndices.append(headerIndex)
                        break
                    headerIndex += 1

        # print(conditionIndices)

        line = f.readline()
        while line:
            line = line.strip().replace(" ","").split(",")
            validTest = False

            if freqRange != None:
                trueFreq = float(line[trueFreqIndex])
                if trueFreq >= freqRange[0] and trueFreq <= freqRange[1]:
                    validTest = True
            else:
                validTest = True

            if validTest:
                meetsConditions = True
                conditionIndex = 0
                for condition in conditions:
                    if line[conditionIndices[conditionIndex]] not in conditions[condition]:
                        meetsConditions = False
                        break
                    conditionIndex += 1

                partialSatisfied = False
                if partialConditions != None:
                    conditionIndex = 0
                    for condition in partialConditions:
                        for possiblePartialValue in partialConditions[condition]:
                            partialSatisfied = False
                            if partialAtStart:
                                if line[partialConditionIndices[conditionIndex]][:len(possiblePartialValue)] == possiblePartialValue:
                                    partialSatisfied = True
                                    break
                            else:
                                if line[partialConditionIndices[conditionIndex]][len(line[partialConditionIndices[conditionIndex]])-len(possiblePartialValue):] == possiblePartialValue:
                                    partialSatisfied = True
                                    break
                        if partialSatisfied == False:
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
        print("Found %s\nMean Time: %ss\nMean Percent Error (Hz): %s\nMean Absolute MIDI Error: %s\nProportion correct (+/- 50 cents): %s\nProportion correct (+/- 50 cents) w/ octave error: %s" % (count, meanTimeAndErrors[0],meanTimeAndErrors[1],meanTimeAndErrors[2],meanTimeAndErrors[3],meanTimeAndErrors[4]))

    return meanTimeAndErrors

## PITCH SHIFTING TEST ANALYSIS

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

def printPerformanceTestAnalysis():
    print("zerocross")
    getMeanTimeAndErrors({"algorithm" : ["zerocross"]}, "csvs/performanceTest.csv", True)
    print()

    print("autocorrelation")
    getMeanTimeAndErrors({"algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True)
    print()

    print("AMDF")
    getMeanTimeAndErrors({"algorithm" : ["AMDF"]}, "csvs/performanceTest.csv", True)
    print()

    print("naiveFT")
    getMeanTimeAndErrors({"algorithm" : ["naiveFT"]}, "csvs/performanceTest.csv", True)
    print()

    print("naiveFTWithPhase")
    getMeanTimeAndErrors({"algorithm" : ["naiveFTWithPhase"]}, "csvs/performanceTest.csv", True)
    print()

    print("cepstrum")
    getMeanTimeAndErrors({"algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True)
    print()

    print("HPS")
    getMeanTimeAndErrors({"algorithm" : ["HPS"]}, "csvs/performanceTest.csv", True)
    print()

def printPerformanceTestAnalysisWithRanges():
    print("zerocross")
    getMeanTimeAndErrors({"algorithm" : ["zerocross"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

    print("autocorrelation")
    getMeanTimeAndErrors({"algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

    print("AMDF")
    getMeanTimeAndErrors({"algorithm" : ["AMDF"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

    print("naiveFT")
    getMeanTimeAndErrors({"algorithm" : ["naiveFT"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

    print("naiveFTWithPhase")
    getMeanTimeAndErrors({"algorithm" : ["naiveFTWithPhase"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

    print("cepstrum")
    getMeanTimeAndErrors({"algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

    print("HPS")
    getMeanTimeAndErrors({"algorithm" : ["HPS"]}, "csvs/performanceTest.csv", True, [50,10000])
    print()

def printAlgorithmTestAnalysisWithRanges(csvFilePath, freqRanges):
    print("zerocross")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["zerocross"]}, csvFilePath, True, freqRange)
        print()

    print("autocorrelation")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["autocorrelation"]}, csvFilePath, True, freqRange)
        print()

    print("AMDF")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["AMDF"]}, csvFilePath, True, freqRange)
        print()

    print("naiveFT")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["naiveFT"]}, csvFilePath, True, freqRange)
        print()

    print("naiveFTWithPhase")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["naiveFTWithPhase"]}, csvFilePath, True, freqRange)
        print()

    print("cepstrum")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["cepstrum"]}, csvFilePath, True, freqRange)
        print()

    print("HPS")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["HPS"]}, csvFilePath, True, freqRange)
        print()

    print("Median")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["median"]}, csvFilePath, True, freqRange)
        print()

    print("trimmedMean")
    for freqRange in freqRanges:
        print("Range %sHz-%sHz" % (freqRange[0], freqRange[1]))
        getMeanTimeAndErrors({"algorithm" : ["trimmedMean"]}, csvFilePath, True, freqRange)
        print()

def algorithmRangesPerformaceAnalysis():
    print("PERFORMANCE TEST ANALYSIS")
    printAlgorithmTestAnalysisWithRanges("csvs/performanceTest.csv", [[20,20000], [50, 10000], [80,1500], [100,1000]])

def algorithmRangesStressAnalysis():
    print("STRESS TEST ANALYSIS")
    printAlgorithmTestAnalysisWithRanges("csvs/stressTest.csv", [[20,20000], [50, 10000], [80,1500], [100,1000]])

def proportionErrorGraphsByHyperparam(csvFilePath, title, verbose, freqRange, algorithm, hyperparamName, hyperparamValues):
    labels = hyperparamValues #ignoring the 'average' label for now
    correctOctaveProportions = []
    octaveErrorProportions = []
    
    for value in labels:
        errors = getMeanTimeAndErrors({"algorithm" : [algorithm], hyperparamName : [value]}, csvFilePath, verbose, freqRange)
        correctOctaveProportions.append(errors[3])
        octaveErrorProportions.append(errors[4])


    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, correctOctaveProportions, width, label='Correct Octave')
    rects2 = ax.bar(x + width/2, octaveErrorProportions, width, label='Allowing +/- 1 Octave')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Proportion')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xlabel(hyperparamName)
    ax.set_xticklabels(labels)
    ax.set_ylim([0,1])
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{0:.3f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def AMDFOptimisationGraphs():
    proportionErrorGraphsByHyperparam("csvs/optimisationTest.csv", "Proportion of correct AMDF predictions (+/- 50 cents) in performanceTest.csv by 'b' value", False, [50,5000], "AMDF", "b", ["0.5","1","2"])

def HPSOptimisationGraphs():
    proportionErrorGraphsByHyperparam("csvs/optimisationTest.csv", "Proportion of correct HPS predictions (+/- 50 cents) in performanceTest.csv by 'numDownsamples' value", False, [50,5000], "HPS", "numDownsamples", ["2","4","6"])

def proportionErrorGraphsByAlgorithm(csvFilePath, title, verbose, freqRange):
    labels = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "naiveFTWithPhase", "cepstrum", "HPS", "median"]#, "trimmedMean"]
    correctOctaveProportions = []
    octaveErrorProportions = []
    
    for algorithm in labels:
        errors = getMeanTimeAndErrors({"algorithm" : [algorithm]}, csvFilePath, verbose, freqRange)
        correctOctaveProportions.append(errors[3])
        octaveErrorProportions.append(errors[4])


    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, correctOctaveProportions, width, label='Correct Octave')
    rects2 = ax.bar(x + width/2, octaveErrorProportions, width, label='+/- One Octave')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Proportion')
    ax.set_title(title)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{0:.3f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def performanceTestGraphs():
    proportionErrorGraphsByAlgorithm("csvs/performanceTest.csv", 'Proportion of correct predictions (+/- 50 cents) in performanceTest.csv', False, [50,5000])

def stressTestGraphs():
    proportionErrorGraphsByAlgorithm("csvs/stressTest.csv", 'Proportion of correct predictions (+/- 50 cents) in stressTest.csv', False, [50,5000])

def getMinMaxTestFreqs():
    for test in ("optimisationTest", "performanceTest", "stressTest"):
        minFreq = float("inf")
        maxFreq = -float("inf")
        trueFreqIndex = 13
        with open("csvs/%s.csv" % (test), "r") as f:
            line = f.readline() #skip past header line
            while line:
                line = f.readline().strip().replace(" ","").split(",")
                if line == [""]:
                    break
                trueFreq = float(line[trueFreqIndex])
                if trueFreq < minFreq:
                    minFreq = trueFreq
                if trueFreq > maxFreq:
                    maxFreq = trueFreq
        
        print("%s\nMin Freq: %s Hz\nMax Freq: %s Hz" % (test, minFreq, maxFreq))

def getPerformanceByInstrumentVSGenerated():
    getMeanTimeAndErrors({"algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True, [20,20000], {"signalType" : ["BBC", "LABS"]})
    getMeanTimeAndErrors({"algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True, [20,20000])

    getMeanTimeAndErrors({"algorithm" : ["AMDF"]}, "csvs/performanceTest.csv", True, [20,20000], {"signalType" : ["BBC", "LABS"]})
    getMeanTimeAndErrors({"algorithm" : ["AMDF"]}, "csvs/performanceTest.csv", True, [20,20000])

    getMeanTimeAndErrors({}, "csvs/performanceTest.csv", True, [20,20000], {"signalType" : ["BBC", "LABS"]})
    getMeanTimeAndErrors({}, "csvs/performanceTest.csv", True, [20,20000])

def allGraphs(errors, xlabel, titles):
    labels = [key for key in errors]#, "trimmedMean"]
    times = []
    percentErrors = []
    absMidiErrors = []
    correctOctaveProportions = []
    octaveErrorProportions = []
    
    for key in labels:
        times.append(errors[key][0])
        percentErrors.append(errors[key][1])
        absMidiErrors.append(errors[key][2])
        correctOctaveProportions.append(errors[key][3])
        octaveErrorProportions.append(errors[key][4])

    def autolabel(rects, dp=3):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate(('{0:.%sf}' % (dp)).format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    # First the time graph
    fig, ax = plt.subplots()
    x = np.arange(len(labels))
    r = ax.bar(x, times)
    autolabel(r, 5)
    ax.set(xlabel=xlabel, ylabel='Time', title=titles[0])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.show()

    # Now the percentage error graph
    fig, ax = plt.subplots()
    x = np.arange(len(labels))
    r = ax.bar(x, percentErrors)
    autolabel(r)
    ax.set(xlabel=xlabel, ylabel='Percentage Error', title=titles[1])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.show()

    # And the absolute MIDI error graph
    fig, ax = plt.subplots()
    x = np.arange(len(labels))
    r = ax.bar(x, absMidiErrors)
    autolabel(r)
    ax.set(xlabel=xlabel, ylabel='Absolute MIDI Number Error', title=titles[2])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.show()

    # Finally the 'correct proportion' graph
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, correctOctaveProportions, width, label='Correct Octave')
    rects2 = ax.bar(x + width/2, octaveErrorProportions, width, label='Allowing +/- 1 Octave')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Proportion')
    ax.set_title(titles[3])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def getAllPerformanceGraphs():
    algorithms = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "naiveFTWithPhase", "cepstrum", "HPS", "median"]#, "trimmedMean"]

    errors = {}

    for algo in algorithms:
        errors[algo] = getMeanTimeAndErrors({"algorithm" : [algo]}, "csvs/performanceTest.csv", True)
        errors[algo][1] *= 100


    allGraphs(errors, "", ["Mean execution times by algorithm in performanceTest.csv", "Mean percentage error by algorithm in performanceTest.csv", "Mean absolute MIDI number error by algorithm in performanceTest.csv", "Proportion of correct predictions by algorithm in performanceTest.csv"])

def getAllStressGraphs():
    algorithms = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "naiveFTWithPhase", "cepstrum", "HPS", "median"]#, "trimmedMean"]

    errors = {}

    for algo in algorithms:
        errors[algo] = getMeanTimeAndErrors({"algorithm" : [algo]}, "csvs/stressTest.csv", True)
        errors[algo][1] *= 100


    allGraphs(errors, "", ["Mean execution times by algorithm in stressTest.csv", "Mean percentage error by algorithm in stressTest.csv", "Mean absolute MIDI number error by algorithm in stressTest.csv", "Proportion of correct predictions by algorithm in stressTest.csv"])

def getGraphsPerSignalType(csvFilePath, freqRange = [20,20000]):
    labels = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "naiveFTWithPhase", "cepstrum", "HPS", "median"]#, "trimmedMean"]
    generatedOctaveErrorProportions = []
    instrumentOctaveErrorProportions = []
    
    for algorithm in labels:
        generatedErrors = getMeanTimeAndErrors({"algorithm" : [algorithm]}, csvFilePath, True, freqRange, {"signalType" : ["sine", "saw", "square", "triangle"]})
        generatedOctaveErrorProportions.append(generatedErrors[4])

        instrumentErrors = getMeanTimeAndErrors({"algorithm" : [algorithm]}, csvFilePath, True, freqRange, {"signalType" : ["BBC", "LABS"]})
        instrumentOctaveErrorProportions.append(instrumentErrors[4])


    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, generatedOctaveErrorProportions, width, label='Generated Signals')
    rects2 = ax.bar(x + width/2, instrumentOctaveErrorProportions, width, label='Instrument Samples')

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Proportion')
    ax.set_title("Proportion of correct predictions by algorithm and signal type in %s (allowing octave errors)" % csvFilePath[5:])
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend(loc="lower right")

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{0:.3f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    autolabel(rects1)
    autolabel(rects2)

    # ax.bar_label(rects1, padding=3)
    # ax.bar_label(rects2, padding=3)

    fig.tight_layout()

    plt.show()

def printCepstrumSineErrors():
    getMeanTimeAndErrors({"signalType" : ["sine"], "algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True)

def getStressGraphByGainBoost():
    labels = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "cepstrum", "HPS", "median"] #ignoring the 'average' label for now
    gainBoostMultipliers = [1,1.5,2] #actually can be [1,1.25,1.5,1.75,2]

    errors = [[]]

    for algo in labels:
        errors[0].append(getMeanTimeAndErrors({"algorithm" : [algo]}, "csvs/performanceTest.csv", True)[4])

    for i, x in enumerate(gainBoostMultipliers):
        errors.append([])
        for algo in labels:
            errors[i+1].append(getMeanTimeAndErrors({"algorithm" : [algo], "extraGain" : [str(x)], "noise" : "0.005"}, "csvs/stressTest.csv", True)[4])

    print(errors)
    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    fig, ax = plt.subplots()

    rects0 = ax.bar(x - 3*width/4, errors[0], width/2, label='No Gain Boost')
    rects1 = ax.bar(x - 1*width/4, errors[1], width/2, label='1')
    rects2 = ax.bar(x + 1*width/4, errors[2], width/2, label='1.5')
    rects3 = ax.bar(x + 3*width/4, errors[3], width/2, label='2')
    # rects4 = ax.bar(x + 3*width/6, errors[4], width/3, label='1.75')
    # rects5 = ax.bar(x + 5*width/6, errors[5], width/3, label='2')

    ax.set_ylabel('Proportion')
    ax.set_title('Proportion of correct predictions by algorithm and gain boost multiplier (allowing for octave errors) in stressTest.csv', fontsize=14)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{:.2f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')

    autolabel(rects0)
    autolabel(rects1)
    autolabel(rects2)
    autolabel(rects3)
    # autolabel(rects4)
    # autolabel(rects5)

    fig.tight_layout()

    plt.show()

def printCepstrumSignalBreakdown():
    print("sine")
    getMeanTimeAndErrors({"signalType" : ["sine"], "algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True)
    print()
    print("saw")
    getMeanTimeAndErrors({"signalType" : ["saw"], "algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True)
    print()
    print("square")
    getMeanTimeAndErrors({"signalType" : ["square"], "algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True)
    print()
    print("triangle")
    getMeanTimeAndErrors({"signalType" : ["triangle"], "algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True)
    print()
    print("sineWithHarmonics")
    getMeanTimeAndErrors({"algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True, [20,20000], {"signalType" : ["sineW"]})

def printCepstrumByGainBoost():
    print("1")
    getMeanTimeAndErrors({"extraGain" : ["1"], "algorithm" : ["cepstrum"]}, "csvs/stressTest.csv", True)
    print()
    print("1.25")
    getMeanTimeAndErrors({"extraGain" : ["1.25"], "algorithm" : ["cepstrum"]}, "csvs/stressTest.csv", True)
    print()
    print("1.5")
    getMeanTimeAndErrors({"extraGain" : ["1.5"], "algorithm" : ["cepstrum"]}, "csvs/stressTest.csv", True)
    print()
    print("1.75")
    getMeanTimeAndErrors({"extraGain" : ["1.75"], "algorithm" : ["cepstrum"]}, "csvs/stressTest.csv", True)
    print()
    print("2")
    getMeanTimeAndErrors({"extraGain" : ["2"]}, "csvs/stressTest.csv", True, [20,20000], {"signalType" : ["sineW"]})

def printAutocorrelationSignalBreakdown():
    print("sine")
    getMeanTimeAndErrors({"signalType" : ["sine"], "algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True)
    print()
    print("saw")
    getMeanTimeAndErrors({"signalType" : ["saw"], "algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True)
    print()
    print("square")
    getMeanTimeAndErrors({"signalType" : ["square"], "algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True)
    print()
    print("triangle")
    getMeanTimeAndErrors({"signalType" : ["triangle"], "algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True)
    print()
    print("sineWithHarmonics")
    getMeanTimeAndErrors({"algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True, [20,20000], {"signalType" : ["sineW"]})

def printMatchingByCanvas():
    e1 = getMeanTimeAndErrors({"blockSize" : ["4096"], "matchingBlockSize" : ["4096"]}, "csvs/matchingTest.csv", True, None, {"signalType" : ["Canvas.wav"]}, False)
    e2 = getMeanTimeAndErrors({"blockSize" : ["8192"], "matchingBlockSize" : ["8192"]}, "csvs/matchingTest.csv", True, None, {"signalType" : ["Canvas.wav"]}, False)
    
    e3 = getMeanTimeAndErrors({"blockSize" : ["4096"], "matchingBlockSize" : ["4096"]}, "csvs/matchingTest.csv", True, None)
    e4 = getMeanTimeAndErrors({"blockSize" : ["8192"], "matchingBlockSize" : ["8192"]}, "csvs/matchingTest.csv", True, None)

    n1, n2, n3, n4 = 61, 51, 111, 96

    withCanvas = [e1[i] + e2[i] for i in range(len(e1))]
    withoutCanvas = [(e3[i]*n3 + e4[i]*n4 - e1[i]*n1 - e2[i]*n2)/(n3 + n4 - n1 - n2) for i in range(len(e1))]
    print("with    canvas: ", withCanvas)
    print("without canvas: ", withoutCanvas)

    return withCanvas, withoutCanvas

def getMatchingByCanvasAllGraphs():
    withCanvas, withoutCanvas = printMatchingByCanvas()
    d = {"Canvas Matching" : withCanvas, "Non-Canvas Matching" : withoutCanvas}
    allGraphs(d, "", ["","","","Proportion of correctly shifted blocks by blockSize (pitch matching)"])

# getStressGraphByGainBoost()
# getGraphsPerSignalType("csvs/performanceTest.csv")
# getAllPerformanceGraphs()
# getPerformanceGraphsPerSignalType()
# getStressGraphByGainBoost()

## PITCH SHIFTING TEST ANALYSIS

def printPitchShiftingTestsAnalysis():
    print("Ratio Test")
    print("TOTAL")
    getMeanTimeAndErrors({}, "csvs/ratioTest.csv", True, None)
    for blockSize in ["4096", "8192"]:
        print("blockSize = %s" % blockSize)
        getMeanTimeAndErrors({"blockSize" : blockSize}, "csvs/ratioTest.csv", True, None)
    print()

    print("Correcting Test")
    print("TOTAL")
    getMeanTimeAndErrors({}, "csvs/correctingTest.csv", True, None)
    for blockSize in ["4096", "8192"]:
        print("blockSize = %s" % blockSize)
        getMeanTimeAndErrors({"blockSize" : blockSize}, "csvs/correctingTest.csv", True, None)
    print()

    print("Matching Test")
    print("TOTAL")
    getMeanTimeAndErrors({}, "csvs/matchingTest.csv", True, None)
    for blockSize in ["4096", "8192"]:
        for matchingBlockSize in ["4096", "8192"]:
            print("(canvas) blockSize = %s, matchingBlockSize = %s" % (blockSize, matchingBlockSize))
            getMeanTimeAndErrors({"blockSize" : blockSize, "matchingBlockSize" : matchingBlockSize}, "csvs/matchingTest.csv", True, None)
    print()

def getPitchShiftingGraphsByBlockSize():
    labels = ["Ratio Shifting", "Pitch Correction", "Pitch Matching"]
    times = [[],[]]
    percentErrors = [[],[]]
    absErrors = [[],[]]
    propErrors = [[],[]]
    propErrorsWithOctave = [[],[]]

    blockSizes = [4096, 8192]
    csvs = ["csvs/ratioTest.csv", "csvs/correctingTest.csv", "csvs/matchingTest.csv"]

    for csv in csvs:
        for i, blockSize in enumerate(blockSizes):
            err = getMeanTimeAndErrors({"blockSize" : [str(blockSize)]}, csv, True, None)
            times[i].append(err[0])
            percentErrors[i].append(err[1])
            absErrors[i].append(err[2])
            propErrors[i].append(err[3])
            propErrorsWithOctave[i].append(err[4])

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{0:.3f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


    # First plot the times
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, times[0], width, label='blockSize = 4096')
    rects2 = ax.bar(x + width/2, times[1], width, label='blockSize = 8192')

    ax.set_ylabel('Time (s)')
    ax.set_title("Execution times for pitch shifting modes by value of blockSize")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()

    # Then plot the percentage errors
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, percentErrors[0], width, label='blockSize = 4096')
    rects2 = ax.bar(x + width/2, percentErrors[1], width, label='blockSize = 8192')

    ax.set_ylabel('Percentage Error')
    ax.set_title("Mean percentage error by pitch shifting mode and value of blockSize")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()

    # Now plot the absolute MIDI errors
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, absErrors[0], width, label='blockSize = 4096')
    rects2 = ax.bar(x + width/2, absErrors[1], width, label='blockSize = 8192')

    ax.set_ylabel('Absolute MIDI number Error')
    ax.set_title("Mean absolute MIDI number error by pitch shifting mode and value of blockSize")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()

    # Now plot proportion of correctly shifted blocks
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, propErrors[0], width, label='blockSize = 4096')
    rects2 = ax.bar(x + width/2, propErrors[1], width, label='blockSize = 8192')

    ax.set_ylabel('Proportion')
    ax.set_title("Proportion of correctly shifted blocks by pitch shifting mode and value of blockSize")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()

    # Finally plot proportion of correctly shifted blocks allowing for octave error
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, propErrorsWithOctave[0], width, label='blockSize = 4096')
    rects2 = ax.bar(x + width/2, propErrorsWithOctave[1], width, label='blockSize = 8192')

    ax.set_ylabel('Proportion')
    ax.set_title("Proportion of correctly shifted blocks by pitch shifting mode and value of blockSize (allowing for octave errors)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()

def getPitchMatchingProportionGraphByBlockSize():
    labels = ["o=4096, m=4096", "o=4096, m=8192", "o=8192, m=4096", "o=8192, m=8192"]
    propErrors = []
    propErrorsWithOctave = []

    blockSizes = [4096, 8192]
    csv = "csvs/matchingTest.csv"

    for i, blockSize in enumerate(blockSizes):
        for j, matchingBlockSize in enumerate(blockSizes):
            err = getMeanTimeAndErrors({"blockSize" : [str(blockSize)], "matchingBlockSize" : [str(matchingBlockSize)]}, csv, True, None)
            propErrors.append(err[3])
            propErrorsWithOctave.append(err[4])

    x = np.arange(len(labels))  # the label locations
    width = 0.35  # the width of the bars

    def autolabel(rects):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate('{0:.3f}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


    # First plot the times
    fig, ax = plt.subplots()
    rects1 = ax.bar(x - width/2, propErrors, width, label='Correct Octave')
    rects2 = ax.bar(x + width/2, propErrorsWithOctave, width, label='Allowing +/- 1 Octave')

    ax.set_ylabel('Proportion')
    ax.set_title("Proportion of correctly shifted blocks by original signal blockSize (o) and matching signal blockSize (m)")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.legend()

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()

    plt.show()   

# getPitchMatchingProportionGraphByBlockSize()

def getGPE(conditions, csvFilePath, verbose=False, freqRange = [20,20000], partialConditions=None, partialAtStart=True):
    '''Returns a list of the form [mean time, mean percentErr, mean absMidiErr, mean correctNote, mean correctNoteWithOctaveErr] 
    where the mean values are taken across csv lines in *csvFilePath* that meet the conditions given in the dictionary *conditions*
        e.g. the conditions dictionary {isCustomFFT : [True]} will average out results of all test cases where isCustomFFT=True
        whereas the dictionary {isCustomFFT : [True, False]} will average out results of all test cases where isCustomFFT=True OR isCustomFFT=False'''
    GPECount = 0
    count = 0

    with open(csvFilePath,"r") as f:
        headers = f.readline().strip().replace(" ","").split(",")
        
        conditionIndices = []
        trueFreqIndex = 13

        for condtionVar in conditions:
            headerIndex = 0
            for header in headers:
                if condtionVar == header:
                    conditionIndices.append(headerIndex)
                    break
                headerIndex += 1

        partialConditionIndices = []

        if partialConditions != None:
            for condtionVar in partialConditions:
                headerIndex = 0
                for header in headers:
                    if condtionVar == header:
                        partialConditionIndices.append(headerIndex)
                        break
                    headerIndex += 1

        # print(conditionIndices)

        line = f.readline()
        while line:
            line = line.strip().replace(" ","").split(",")
            validTest = False

            if freqRange != None:
                trueFreq = float(line[trueFreqIndex])
                if trueFreq >= freqRange[0] and trueFreq <= freqRange[1]:
                    validTest = True
            else:
                validTest = True

            if validTest:
                meetsConditions = True
                conditionIndex = 0
                for condition in conditions:
                    if line[conditionIndices[conditionIndex]] not in conditions[condition]:
                        meetsConditions = False
                        break
                    conditionIndex += 1

                partialSatisfied = False
                if partialConditions != None:
                    conditionIndex = 0
                    for condition in partialConditions:
                        for possiblePartialValue in partialConditions[condition]:
                            partialSatisfied = False
                            if partialAtStart:
                                if line[partialConditionIndices[conditionIndex]][:len(possiblePartialValue)] == possiblePartialValue:
                                    partialSatisfied = True
                                    break
                            else:
                                if line[partialConditionIndices[conditionIndex]][len(line[partialConditionIndices[conditionIndex]])-len(possiblePartialValue):] == possiblePartialValue:
                                    partialSatisfied = True
                                    break
                        if partialSatisfied == False:
                            meetsConditions = False
                            break
                        conditionIndex += 1

                if meetsConditions:
                    count += 1
                    if float(line[-4]) > 0.2:
                        GPECount += 1

            line = f.readline()
            line1 = False
        
    if count == 0:
        if verbose:
            print("No lines found to match condition %s" % (conditions))
        return -1
    
    GPE = GPECount/count

    if verbose:
        print("Found %s\n GPE = %s" % (count, GPECount/count))

    return GPE

def printPerformanceTestGPE():
    GPEs = []
    print("zerocross")
    GPEs.append(getGPE({"algorithm" : ["zerocross"]}, "csvs/performanceTest.csv", True))
    print()

    print("autocorrelation")
    GPEs.append(getGPE({"algorithm" : ["autocorrelation"]}, "csvs/performanceTest.csv", True))
    print()

    print("AMDF")
    GPEs.append(getGPE({"algorithm" : ["AMDF"]}, "csvs/performanceTest.csv", True))
    print()

    print("naiveFT")
    GPEs.append(getGPE({"algorithm" : ["naiveFT"]}, "csvs/performanceTest.csv", True))
    print()

    print("naiveFTWithPhase")
    GPEs.append(getGPE({"algorithm" : ["naiveFTWithPhase"]}, "csvs/performanceTest.csv", True))
    print()

    print("cepstrum")
    GPEs.append(getGPE({"algorithm" : ["cepstrum"]}, "csvs/performanceTest.csv", True))
    print()

    print("HPS")
    GPEs.append(getGPE({"algorithm" : ["HPS"]}, "csvs/performanceTest.csv", True))
    print()

    print("HPS")
    GPEs.append(getGPE({"algorithm" : ["median"]}, "csvs/performanceTest.csv", True))
    print()

    return GPEs

def performanceGPEGraph():
    def autolabel(rects, dp=1):
        """Attach a text label above each bar in *rects*, displaying its height."""
        for rect in rects:
            height = rect.get_height()
            ax.annotate(('{0:.%sf}' % (dp)).format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom')


    GPEs = printPerformanceTestGPE()
    GPEs = [x*100 for x in GPEs]
    labels = ["zerocross", "autocorrelation", "AMDF", "naiveFT", "naiveFTWithPhase", "cepstrum", "HPS", "median"]#, "trimmedMean"]

    fig, ax = plt.subplots()
    x = np.arange(len(labels))
    r = ax.bar(x, GPEs)
    autolabel(r, 1)
    ax.set(xlabel="", ylabel='Gross Pitch Error (%)', title="Gross pitch error (GPE) by algorithm in performanceTest.csv")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    plt.show()

performanceGPEGraph()

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

                errors = [getPercentageError(expectedFreq,actualFreq), getAbsoluteMIDIError(expectedFreq, actualFreq), isWithin100Cents(expectedFreq, actualFreq), isWithin100CentsWithOctaveError(expectedFreq, actualFreq)]

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