from math import pi, sin, asin, floor

def getSine(freq, length, sampleRate):
    '''returns a sine wave signal as a list of floats
    freq (float)     --  frequency of signal required in Hz
    length (int)     --  length of signal required
    samlpeRate (int) --  sample rate of signal'''
   
    return [sin(2*pi*i*freq/(1.0*sampleRate)) for i in range(length)]

def getSaw(freq, length, sampleRate):
    '''returns a sawtooth wave signal as a list of floats
    freq (float)     --  frequency of signal required in Hz
    length (int)     --  length of signal required
    samlpeRate (int) --  sample rate of  signal'''

    return [2*(i*freq/((1.0*sampleRate)) - floor(0.5 + i*freq/((1.0*sampleRate)))) for i in range(length)]

def getSquare(freq, length, sampleRate):
    '''returns a square wave signal as a list of floats
    freq (float)     --  frequency of signal required in Hz
    length (int)     --  length of signal required
    samlpeRate (int) --  sample rate of  signal'''

    return [1.0 if sin(2*pi*i*freq/(1.0*sampleRate)) >= 0 else -1.0 for i in range(length)]

def getTriangle(freq, length, sampleRate):
    '''returns a triangle wave signal as a list of floats
    freq (float)     --  frequency of signal required in Hz
    length (int)     --  length of signal required
    samlpeRate (int) --  sample rate of  signal'''

    return [(2/2*pi)*asin(sin(2*pi*i*freq/(1.0*sampleRate))) for i in range(length)]

def getSineWithHarmonics(freq, length, sampleRate, numHarmonics):
    waveform = [0 for i in range(length)]
    for i in range(1, numHarmonics+1):
        harmonic = getSine(freq*i, length, sampleRate)
        for j in range(length):
            waveform[j] += harmonic[j] * (1/i)
    return waveform