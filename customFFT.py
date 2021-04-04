import cmath

def fft(signal, fullLength=False):
    bins = [re+0j for re in signal]
    fftRecurse(bins)
    if fullLength:
        return bins
    return bins[:1+len(bins)//2] #to conform to np.fft practices

def fftRecurse(data):
    N = len(data)
    
    if N > 1:
        even = data[0:N:2]
        odd  = data[1:N:2]
    
        fftRecurse(even)
        fftRecurse(odd)

        for k in range(N//2):
            t = cmath.exp(-2j*cmath.pi*k/N) * odd[k]
            data[k] = even[k] + t
            data[k + N//2] = even[k] - t
    

def ifft(bins, fullLength=False):
    conjugateBins = [x.conjugate() for x in bins]
    return [x.conjugate()/len(bins) for x in fft(conjugateBins, fullLength)]