from predict import zerocross, autocorrelation, AMDF, naiveFT, cepstrum, HPS

class pitchProfile:
    def __init__(signal, detectionMode):
        this.signal = signal
        this.detectionMode = detectionMode