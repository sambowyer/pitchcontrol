#include "PitchControl.h"
#include "IPlug_include_in_plug_src.h"
#include "IControls.h"
#include "IPlugProcessor.h"
#include <iostream>
#include <stdlib.h>
#include <cmath>
//#include "../../WDL/fft.h"
#include <complex>

#define PI 3.14159265

//const int blockMemoryNo = 4;
//const int blockSize = 256;
//const int blockMemorySize = blockMemoryNo * blockSize;
//double* blockMemory = new double[blockMemorySize];
//int blockMemoryCounter = 0;

const int bufferSize = 32768/32; // = 2^15
int bufferHeadIndex = 0; //index of 'first' element in the circular buffer
int bufferTailIndex = -1; //index of 'last' element in circular buffer
double *buffer = new double[bufferSize];

const int stackSize = 256;
int stackCounter = 0;
double* stack = new double [stackSize];

//compare function taken from http://www.cplusplus.com/reference/cstdlib/qsort/
int compare (const void * a, const void * b)
{
  return ( *(double*)a - *(double*)b );
}

int getBufferIndex(int rawIndex){
  return (rawIndex + bufferHeadIndex) % bufferSize;
}

double bufferGet(int index){
  return buffer[(bufferHeadIndex + index) % bufferSize];
}

void addToBuffer(double input){
  //don't want to add a long string of zeros if no signal is really passing
  if (input != 0 ){//or buffer[bufferTailIndex] != 0){
    bufferTailIndex = ++bufferTailIndex % bufferSize;
    buffer[bufferTailIndex] = input;
    if (bufferTailIndex == bufferHeadIndex){
      bufferHeadIndex = ++bufferHeadIndex % bufferSize;
    }
  }
}

int getBufferCapacity(){
  return ((bufferTailIndex + bufferSize - bufferHeadIndex) % bufferSize) + 1;
}

double getTrimmedMean(double* data, float trimSize){
    double sum = 0;
    int n = 0;
    const int size = sizeof(*data)/sizeof(double);
    double* dataCopy = new double [size];
    for (int i=0; i<size; i++){
        dataCopy[i] = data[i];
    }
    //could implement my own quicksort here (why though? wouldn't be any faster/lighter)
    qsort(dataCopy, size, sizeof(double), compare);
    for (int i=floor(size*trimSize); i<ceil(size*(1-trimSize)); i++){
        if (dataCopy[i] > 0){
            sum += dataCopy[i];
            n++;
        }
    }
    return sum/n;
}

double getMidiNoteWithCents(double frequency){
    //return log10(frequency/27.5) / log10(pow(2, 1/12));
    return 69 + 12*log2(frequency/440);
}

const char* getNoteName(double frequency){
    int midiNote = (int) round(getMidiNoteWithCents(frequency));
    int midiOctave = midiNote/12;

    std::string temp;
    switch (midiNote % 12){
        case 0:
            temp = "A";
            break;
        case 1:
            temp = "A#";
            break;
        case 2:
            temp = "B";
            break;
        case 3:
            temp = "C";
            break;
        case 4:
            temp = "C#";
            break;
        case 5:
            temp = "D";
            break;
        case 6:
            temp = "D#";
            break;
        case 7:
            temp = "E";
            break;
        case 8:
            temp = "F";
            break;
        case 9:
            temp = "F#";
            break;
        case 10:
            temp = "G";
            break;
        case 11:
            temp = "G#";
            break;
        default:
            temp = "??";
    }
    temp += std::to_string(midiOctave);
    char const *result = temp.c_str();
    printf(result);
    return result;
}

int getCents(double frequency){
    double midiNote = getMidiNoteWithCents(frequency);
    return round((midiNote - (long) midiNote) * 100);
}


void fftForward(std::complex<double>* inputs, int N, int s, std::complex<double>* bins){
    std::complex<double> i = std::complex<double>(0.0,1.0);
    std::complex<double> t;
    if (N==1){
        bins[0] = inputs[0];
    }
    else {
        fftForward(inputs, N/2, 2*s, bins);
        fftForward(inputs + s, N/2, 2*s, bins + N/2);

        for(int k=0; k < N/2; k++){
            t = bins[k];
            bins[k] = t + std::exp(-2*PI*i*(k*1.0)/(N*1.0));
            bins[k + N/2] = t - std::exp(-2*PI*i*(k*1.0)/(N*1.0));
        }
    }
}

void fftForwardReal(double* inputs, int N, int s, std::complex<double>* bins){
    std::complex<double>* complex = new std::complex<double>[N];
    for (int i = 0; i < N; i++){
        complex[i] = std::complex<double>(inputs[i],0);
    }
    fftForward(complex, N, s, bins);
}


void fftInverse(std::complex<double>* bins, int N, std::complex<double>* output){
    for (int i = 0; i < N; i++){
        bins[i] = conj(bins[i]);
    }
    fftForward(bins, N, 1, output);
    for (int i = 0; i < N; i++){
        bins[i] = conj(bins[i])/(N*1.0);
    }
}

void fftInverseReal(double* bins, int N, std::complex<double>* output){
    std::complex<double>* complex = new std::complex<double>[N];
    for (int i = 0; i < N; i++){
        complex[i] = std::complex<double>(bins[i],0);
    }
    fftInverse(complex, N, output);
}

double zeroCrossPredict(double* inputs, int nChans, int length, double sampleRate)
{
    int first0CrossIndex = -1;
    int last0CrossIndex = length;
    int zeroCrossCount = 0;
//    bool positive = inputs[0] > 0;
    bool positive = bufferGet(0) > 0;
    
    for (int s = 0; s < getBufferCapacity(); s++) {
      //for (int c = 0; c < nChans; c++) {
        //outputs[c][s] = inputs[c][s];
//        if (inputs[s] > 0 != positive){
        if (s<50){
          printf("%f\t%f\n", buffer[(bufferTailIndex-length+s+bufferSize)%bufferSize], inputs[s]);
        }
        if (bufferGet(s) > 0 != positive){
            zeroCrossCount++;
            positive = !positive;
              
            if(first0CrossIndex == -1){
              first0CrossIndex = s;
            } else {
              last0CrossIndex = s;
          }
        }
      //}
    }
    double freq = sampleRate*0.5*(zeroCrossCount-1)/(last0CrossIndex-first0CrossIndex);
    if(zeroCrossCount>1){
      printf("%d\t%d\t%d\t%f\n", length, bufferHeadIndex, bufferTailIndex, freq);
    }
    return freq;
}

double autoCorrelationPredict(double* inputs, int nChans, int nFrames, double sampleRate)
{
//    //have to choose size of this array carefully as it limits range of estimates possible
//    int maxComparisionDistance = blockMemorySize/4;
//
//    //each mth bin corresponds to the autocorrelation sum:- sum of x(i)x(i+m) forall i
//    double* bins = new double [maxComparisionDistance];
//
//    double sum;
//    int counter;
//
//    //for (int s = 0; s < nFrames; s++) {
//      for (int c = 0; c < nChans; c++) {
//          for (int m = 1; m < maxComparisionDistance+1; m++) {
//              //outputs[c][m] = inputs[c][m];
//              sum = 0;
//              counter = 0;
//              for (int i = 0; i < nFrames; i += m){
//                  sum += blockMemory[(blockMemoryCounter * blockSize + i) % blockMemorySize]*blockMemory[(blockMemoryCounter * blockSize + i + m) % blockMemorySize];
//                  counter++;
//              }
//              bins[m] = sum/(counter*1.0);
//          }
//      }
//    //}
//
//    double maxCorrelation = 0.0;
//    int maxM = 0;
//    for (int m = 0; m < maxComparisionDistance; m++){
//        if (bins[m] > maxCorrelation){
//            maxCorrelation = bins[m];
//            maxM = m;
//        }
//    }
//
//    double freq = sampleRate / maxM;
//    printf("%f\n", freq);
//    return freq;
}

double cepstrumPredict(double* inputs, int nFrames, double sampleRate)
{
    
////    WDL_fft_init();
//    double* signal = new double[blockMemorySize];
//    for (int i = 0; i < blockMemorySize; i++){
//        signal[i] = blockMemory[i];
////        for (int j = 0; j < nChans; j++){
////            outputs[j][i] = outputs[j][i];
////        }
//    }
//    std::complex<double>* bins = new std::complex<double>[blockMemorySize];
//    fftForwardReal(signal, blockMemorySize, 1, bins);
//
////
////    //forward fft
////    WDL_real_fft((WDL_FFT_REAL*) signal, nFrames, 0);
////
//    //scale back
//    for (int i = 0; i < blockMemorySize; ++i)
//    {
//            bins[i] /= blockMemorySize;
//    }
////
////    // Bins are stored out of order, so use permutation table to fix.
////    const int* order = WDL_fft_permute_tab(nFrames / 2);
////
////    printf("Bin\tFrequency\tMagnitude\tPhase\n");
//    std::complex<double> bin;
//    for (int i = 0; i < blockMemorySize ; ++i)
//    {
////        WDL_FFT_COMPLEX* bin = (WDL_FFT_COMPLEX*)signal + order[i];
//        bin = bins[i];
//        double re, im;
//        if (i == 0)
//        {
//            // DC (0 Hz)
//            re = bin.real();
//            im = 0.0;
//        }
//        else if (i == blockMemorySize / 2)
//        {
//            // Nyquist frequency
//            re = signal[1]; // i.e. DC bin->im
//            im = 0.0;
//        }
//        else
//        {
//            re = bin.real();
//            im = bin.imag();
//        }
//
//        //const double mag = sqrt(re*re + im*im);
//        signal[i] = log(re*re + im*im);
//        //const double phase = atan2(im, re);
//
//        //const double freq = (double)i / nFrames * sampleRate;
//        //printf("%d\t%f\t%f\t%f\n", i, freq, mag, phase);
//    }
//    fftInverseReal(signal, blockMemorySize, bins);
//    for (int i = 0; i < blockMemorySize; i++){
//        double re = bins[i].real();
//        double im = bins[i].imag();
//        const double mag = sqrt(re*re + im*im);
//        const double freq = (double)i / blockMemorySize * sampleRate;
//        printf("%d\t%f\t%f\n", i, freq, mag);
//    }
//
    std::complex<double>* bins = new std::complex<double>[nFrames];
    fftForwardReal(inputs, nFrames, 1, bins);
    for (int i = 0; i < nFrames; i++){
        inputs[i] = log(bins[i].real()*bins[i].real() + bins[i].imag()*bins[i].imag());
    }
    fftForwardReal(inputs, nFrames, 1, bins);
    double maxMag = -1.0;
    int maxMagIndex = -1;
    double mag;
    
    for (int i = 1 ; i < nFrames; i++){
        mag = bins[i].real()*bins[i].real() + bins[i].imag()*bins[i].imag();
        printf("%d\t%f\n", i, mag);
        if (mag > maxMag){
            maxMag = mag;
            maxMagIndex = i;
        }
    }
    printf("max i = %d\n", maxMagIndex);
    return sampleRate*maxMagIndex/nFrames;
}

PitchControl::PitchControl(const InstanceInfo& info)
: Plugin(info, MakeConfig(kNumParams, kNumPresets))
{
  GetParam(kGain)->InitDouble("Gain", 0., 0., 100.0, 0.01, "%");

#if IPLUG_EDITOR // http://bit.ly/2S64BDd
  mMakeGraphicsFunc = [&]() {
    return MakeGraphics(*this, PLUG_WIDTH, PLUG_HEIGHT, PLUG_FPS, GetScaleForScreen(PLUG_HEIGHT));
  };
  
  mLayoutFunc = [&](IGraphics* pGraphics) {
    pGraphics->AttachCornerResizer(EUIResizerMode::Scale, false);
    pGraphics->AttachPanelBackground(COLOR_GRAY);
    pGraphics->LoadFont("Roboto-Regular", ROBOTO_FN);
    const IRECT b = pGraphics->GetBounds();
    pGraphics->AttachControl(new ITextControl(b.GetCentredInside(100).GetVShifted(-200).GetPadded(150), "Pitch Detection", IText(75)));
    //pGraphics->AttachControl(new IVKnobControl(b.GetCentredInside(100).GetVShifted(-100), kGain));
    //pGraphics->AttachControl(new IVKnobControl(b.GetCentredInside(100).GetVShifted(-100), kCtrlTagRTText/8.8));
    //pGraphics->AttachControl(new ITextControl(b.GetMidVPadded(100).GetVShifted(100), getNoteName(kCtrlTagRTText), IText(50)))->SetDirty();
    pGraphics->AttachControl(new IRTTextControl<1, float>(b.GetMidVPadded(100), "%0.2f Hz", "", "", IText(50)), kCtrlTagRTText);
    pGraphics->AttachControl(new IRTTextControl<1, float>(b.GetMidVPadded(100).GetVShifted(100), "Closest in tune note: %0.2f Hz", "", "", IText(20)), kCtrlTagRTText2);
  };
#endif
}

#if IPLUG_DSP
void PitchControl::OnIdle()
{
  mRTTextSender.TransmitData(*this);
  mRTTextSender2.TransmitData(*this);
}
void PitchControl::ProcessBlock(sample** inputs, sample** outputs, int nFrames)
{
  const double gain = GetParam(kGain)->Value() / 100.;
  int nChans = NOutChansConnected();
//  printf("%d\n", nChans);
  
  double* signal = new double[nFrames];
    
  for (int s = 0; s < nFrames; s++) {
    for (int c = 0; c < nChans; c++) {
      outputs[c][s] = inputs[c][s] * gain;
    }
//    buffer[getBufferIndex(s)] = (double) inputs[0][s];
//    bufferHeadIndex++;
//    if (bufferHeadIndex >= bufferSize){
//      bufferHeadIndex = 0;
//    }
    signal[s] = inputs[0][s];
    addToBuffer(inputs[0][s]);
  }
  
  double freq = zeroCrossPredict(signal, nChans, nFrames, GetSampleRate());
//  double freq = zeroCrossPredict(buffer, nChans, getBufferCapacity(), GetSampleRate()); //doesn't work but should
  //double freq = autoCorrelationPredict(buffer, nChans, nFrames, GetSampleRate());
  //double freq = cepstrumPredict(buffer, nFrames, GetSampleRate());
  
  stack[stackCounter] = freq;
  stackCounter = (stackCounter + 1) % stackSize;

  //send freq over to the GUI part of the code
  float estimate = (float) getTrimmedMean(stack, 0.2);
    if (estimate > 0){
      mLastOutputData.vals[0] = estimate;
      mRTTextSender.PushData(mLastOutputData);
        
      mLastOutputData2.vals[0] = (float) pow(2, (round(getMidiNoteWithCents(estimate))-69)/12)*440;
      mRTTextSender2.PushData(mLastOutputData2);
    }
}
#endif
