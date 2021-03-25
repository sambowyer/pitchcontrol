import testing, signalGenerator

#32 different frequencies
frequencies = [50,75,100,125,150,200,250,300,350,400,450,500,600,700,800,900,1000,1500,2000,2500,3000,4000,5000,6000,7000,8000,9000,10000,12500,15000,17500,20000]
#just 2 different sample rates
sampleRates = [44100,22050]

# testing.testAllAlgorithmsToCSV(signalGenerator.getSaw(440,2048,44100), 44100, "saw", 440, "csvs/generatedSignalsTest.csv")

for sampleRate in sampleRates:
    for freq in frequencies:

        #sine
        signal = signalGenerator.getSine(freq, 2048, sampleRate)
        testing.testAllAlgorithmsToCSV(signal, sampleRate, "sine", freq, "csvs/generatedSignalsTest.csv")

        #saw
        signal = signalGenerator.getSaw(freq, 2048, sampleRate)
        testing.testAllAlgorithmsToCSV(signal, sampleRate, "saw", freq, "csvs/generatedSignalsTest.csv")

        #square
        signal = signalGenerator.getSquare(freq, 2048, sampleRate)
        testing.testAllAlgorithmsToCSV(signal, sampleRate, "square", freq, "csvs/generatedSignalsTest.csv")

        #triangle
        signal = signalGenerator.getTriangle(freq, 2048, sampleRate)
        testing.testAllAlgorithmsToCSV(signal, sampleRate, "triangle", freq, "csvs/generatedSignalsTest.csv")

        #sineWith10Harmomics
        signal = signalGenerator.getSineWithHarmonics(freq, 2048, sampleRate, 10)
        testing.testAllAlgorithmsToCSV(signal, sampleRate, "sineWith10Harmonics", freq, "csvs/generatedSignalsTest.csv")

        #sineWith20Harmonics
        signal = signalGenerator.getSineWithHarmonics(freq, 2048, sampleRate, 20)
        testing.testAllAlgorithmsToCSV(signal, sampleRate, "sineWith20Harmonics", freq, "csvs/generatedSignalsTest.csv")
