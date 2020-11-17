# Created by Sam Bowyer 17/11/20
#
# A test for finding the 'true' frequency amongst a list of estimate frequencies generated from a
#   zero-crossing algorithm (which has a substantial amount of noise and outliers) on a pure
#   sine wave signal of 440Hz.
#
# A variety of techinques are used to attempt to find this 'true' frequency including the different
#   Pythagorean means as well as excluding estimates which are:
#           - A certain distance away from the (arithmetic) mean of the whole dataset
#             (with the distance given as a proportion of the data's standard deviation - sigma -
#             e.g. excluding all estimates which lie more than 0.01*sigma away from the mean)
#           - At an extreme end of the dataset (e.g. in the bottom or top 10% of all data)
#             N.B. the above exmaple would be achieved by calling analysePercentTrim(..., trim=20)
#
#               ------- TODO --------
# - fix standard deviation
# - generalise tests (especially the rolling avg ones)
# - find optimal rolling avg and trim setting
#       - 20% or 25% seems good for now but once standard deviation is fixed that might be more useful
#         (or possibly a combination? percentage first (for outliers) then standard deviation (for noise)

import math
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import colors
from matplotlib.ticker import PercentFormatter

readings = []
with open("0Cross-440hz-readings.csv", "r") as f:
     for line in f:
        readings.append(float(line))
        
def getMean(x):
    sum = 0
    for i in x:
        sum += i
    return sum/len(x)

def analyseNoTrim(data, n, output=True):
    sqSum = 0
    sum = 0
    geoMean = 1.0
    harmSum = 0
    
    for i, val in enumerate(data):
        if (i<n):
            sqSum += val*val
            sum += val
            geoMean *= val
            harmSum += 1/val
            
    mean = sum/n
    sigma = (sqSum-((sum/n)**2))**0.5

    if (output):
        print("--------   RAW DATA (no trimming) --------")
        print("Source:            440Hz")
        print("Arithmetic Mean  : %s" % (sum/n))
        print("Std Deviation    : %s" % (sigma))
        print("Geometric  Mean  : %s" % (geoMean**(1/n)))
        print("Harmonic   Mean  : %s" % (n/harmSum))
        print("min              : %s" % (min(data)))
        print("max              : %s" % (max(data)))
        
        print("\n")
    
    return [mean, sigma]

def analyseSigmaTrim(data, n, mean, sigma, trim, output=True):
    sqSum = 0
    sum = 0
    geoMean = 1.0
    harmSum = 0
    validN = 0
    trimmedData = []
    
    for val in data:
        if ((validN < n) & (abs(val - mean) < sigma*trim)):
            validN += 1
            sqSum += val*val
            sum += val
            geoMean *= val**(1/n)
            harmSum += 1/val
            trimmedData.append(val)
    
    if (output):
        mean = sum/n
        sigma = (sqSum-((sum/n)**2))**0.5
    
        print("--------      Trim of Sigma*%s    --------" % (trim))
        print("Source:            440Hz")
        print("Arithmetic Mean  : %s" % (sum/validN))
        print("Std Deviation    : %s" % (sigma))
        print("Geometric  Mean  : %s" % (geoMean))
        print("Harmonic   Mean  : %s" % (validN/harmSum))
        print("min              : %s" % (min(trimmedData)))
        print("max              : %s" % (max(trimmedData)))
        print("valid data       : %s/%s" % (validN, min([n, len(data)])))
        
        print("\n")
    
    return trimmedData
    
def analysePercentTrim(data, n, mean, trim, output=True):
    sqSum = 0
    sum = 0
    geoMean = 1.0
    harmSum = 0
    validN = 0
    
    preTrimmedData = data[:n]
    preTrimmedLength = len(preTrimmedData)
    preTrimmedData.sort()
    
    trimmedData = preTrimmedData[math.ceil(preTrimmedLength*0.01*trim) : math.floor(preTrimmedLength - preTrimmedLength*0.01*trim)]
    
    if (output):
        for val in trimmedData:
            validN += 1
            sqSum += val*val
            sum += val
            geoMean *= val**(1/n)
            harmSum += 1/val
                
        mean = sum/n
        sigma = (sqSum-((sum/n)**2))**0.5

        print("--------        Trim of %s       --------" % (trim))
        print("Source:            440Hz")
        print("Arithmetic Mean  : %s" % (sum/validN))
        print("Std Deviation    : %s" % (sigma))
        print("Geometric  Mean  : %s" % (geoMean))
        print("Harmonic   Mean  : %s" % (validN/harmSum))
        print("min              : %s" % (min(trimmedData)))
        print("max              : %s" % (max(trimmedData)))
        print("valid data       : %s/%s" % (len(trimmedData), min([n, len(data)])))
        
        print("\n")
    
    return trimmedData
    
    
def rollingAvg(data, n, period, trimType="", trimParam=None):
    stack = [None] * period
    stackIndex = 0
    rollingAvgs = [None] * (len(data)-period+1)
    
    mean, sigma = analyseNoTrim(readings, n, output=False)
        
    for i in range(len(data)-period+1):
        stack[i % period] = data[i]
        #print(stack)
        if (None not in stack):
            stack[stackIndex] = data[i]
            if (trimType.lower() == "sigma"):
                rollingAvgs[i] = getMean(analyseSigmaTrim(stack, n, mean, sigma, trimParam, output=False))
            elif (trimType.lower() == "percent"):
                rollingAvgs[i] = getMean(analysePercentTrim(stack, n, mean, trimParam, output=False))
            else:
                rollingAvgs[i] = getMean(stack)
            stackIndex = (stackIndex+1) % period
                
    return [i for i in rollingAvgs if i is not None]

#Analysis on all 766 readings
def test766():
    print("--------         Tests using      --------")
    print("--------         766 readings     --------")
    mean, sigma = analyseNoTrim(readings, 766)
    trimmedReadingSigs0_01 = analyseSigmaTrim(readings, 766, mean, sigma, 0.01)
    trimmedReadingsSig0_005 = analyseSigmaTrim(readings, 766, mean, sigma, 0.005)
    trimmedReadingsPercent10 = analysePercentTrim(readings, 766, mean, 10)
    trimmedReadingsPercent20 = analysePercentTrim(readings, 766, mean, 20)

    print("\n")

#Analysis on 500 readings
def test500():
    print("--------         Tests using      --------")
    print("--------         500 readings     --------")
    mean, sigma = analyseNoTrim(readings, 500)
    trimmedReadingSigs0_01 = analyseSigmaTrim(readings, 500, mean, sigma, 0.01)
    trimmedReadingsSig0_005 = analyseSigmaTrim(readings, 500, mean, sigma, 0.005)
    trimmedReadingsPercent10 = analysePercentTrim(readings, 500, mean, 10)
    trimmedReadingsPercent20 = analysePercentTrim(readings, 500, mean, 20)

    print("\n")

# --------- TODO -------------
#Analysis on 10 readings at a time
#(@ sample rate of 44.1kHz w/ blocks of 256 samples, each block takes ~0.0058s (= 256 / 44100)
# so 10 blocks will give the tuner completely new data every 0.058 seconds - though we could
# stagger the data in a fixed-sized stack structure and keep the tuner updated with a rolling average)
def test766Rolling10():
    print("--------         Tests using      --------")
    print("--------         766 readings     --------")
    print("--------         10 at a time     --------")
    rollingAvg10NoTrim = rollingAvg(readings, 766, 10)
    analyseNoTrim(rollingAvg10NoTrim, len(rollingAvg10NoTrim))
    rollingAvg10Sig0_01 = rollingAvg(readings, 766, 10, "sigma", 0.01)
    analyseNoTrim(rollingAvg10Sig0_01, len(rollingAvg10Sig0_01))
    rollingAvg10Sig0_001 = rollingAvg(readings, 766, 10, "sigma", 0.005)
    analyseNoTrim(rollingAvg10Sig0_001, len(rollingAvg10Sig0_001))
    rollingAvg10Percent10 = rollingAvg(readings, 766, 10, "percent", 10)
    analyseNoTrim(rollingAvg10Percent10, len(rollingAvg10Percent10))
    rollingAvg10Percent20 = rollingAvg(readings, 766, 10, "percent", 20)
    analyseNoTrim(rollingAvg10Percent20, len(rollingAvg10Percent20))

    print("\n")

#Analysis on 20 readings at a time
#(@ sample rate of 44.1kHz w/ blocks of 256 samples, each block takes ~0.0058s
# so 20 blocks will give the tuner completely new data every 0.106 seconds)
def test766Rolling20():
    print("--------         Tests using      --------")
    print("--------         766 readings     --------")
    print("--------         20 at a time     --------")
    
    rollingAvg10NoTrim = rollingAvg(readings, 766, 20)
    #print(rollingAvg10NoTrim)
    analyseNoTrim(rollingAvg10NoTrim, len(rollingAvg10NoTrim))
    
    print("sigma 0.01 trim")
    rollingAvg10Sig0_01 = rollingAvg(readings, 766, 20, "sigma", 0.01)
    analyseNoTrim(rollingAvg10Sig0_01, len(rollingAvg10Sig0_01))
    
    print("sigma 0.005 trim")
    rollingAvg10Sig0_001 = rollingAvg(readings, 766, 20, "sigma", 0.005)
    analyseNoTrim(rollingAvg10Sig0_001, len(rollingAvg10Sig0_001))
    
    print("10 percent trim")
    rollingAvg10Percent10 = rollingAvg(readings, 766, 20, "percent", 10)
    analyseNoTrim(rollingAvg10Percent10, len(rollingAvg10Percent10))
    
    print("20 percent trim")
    rollingAvg10Percent20 = rollingAvg(readings, 766, 32, "percent", 25)
    print(rollingAvg10Percent20)
    analyseNoTrim(rollingAvg10Percent20, len(rollingAvg10Percent20))
    
    print("\n")

#test766()
#test500()
#test766Rolling10()
test766Rolling20()

#readings.sort()
#print(readings)


# Histogram
HISTOGRAM = False;

if HISTOGRAM:
    fig, ax = plt.subplots(tight_layout=True)

    # We can set the number of bins with the `bins` kwarg
    ax.hist(readings, bins=1000)
    plt.show()
