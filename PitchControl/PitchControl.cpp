#include "PitchControl.h"
#include "IPlug_include_in_plug_src.h"
#include "IControls.h"
#include "IPlugProcessor.h"
#include <iostream>
#include <stdlib.h>
#include <cmath>
 
const int stackSize = 64;
int stackCounter = 0;
double* stack = new double [stackSize];

//compare function taken from http://www.cplusplus.com/reference/cstdlib/qsort/
int compare (const void * a, const void * b)
{
  return ( *(double*)a - *(double*)b );
}

double getTrimmedMean(double* data, float trimSize){
    double sum = 0;
    int n = 0;
    const int size = sizeof(*data)/sizeof(double);
    double* dataCopy = new double [size];
    for (int i=0; i<size; i++){
        dataCopy[i] = data[i];
    }
    //could implement my own quicksort here
    qsort(dataCopy, size, sizeof(double), compare);
    for (int i=floor(size*trimSize); i<ceil(size*(1-trimSize)); i++){
        sum += dataCopy[i];
        n++;
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
  const int nChans = NOutChansConnected();
    
  int first0CrossIndex = -1;
  int last0CrossIndex = nFrames;
  int zeroCrossCount = 0;
  bool positive = inputs[0][0] > 0;
  
  for (int s = 0; s < nFrames; s++) {
    for (int c = 0; c < nChans; c++) {
      outputs[c][s] = inputs[c][s] * gain;
        if (inputs[c][s] > 0 != positive){
            zeroCrossCount++;
            positive = !positive;
            
            if(first0CrossIndex == -1){
                first0CrossIndex = s;
            } else {
                last0CrossIndex = s;
            }
        }
    }
  }
  double freq = GetSampleRate()*0.5*(zeroCrossCount-1)/(last0CrossIndex-first0CrossIndex) ;
  if(zeroCrossCount>1){
    //printf("%f\n", freq);
  }
  stack[stackCounter] = freq;
  stackCounter = (stackCounter + 1)/stackSize;

  //send freq over to the GUI part of the code
  mLastOutputData.vals[0] = (float) getTrimmedMean(stack, 0.25);
  mRTTextSender.PushData(mLastOutputData);
    
  mLastOutputData2.vals[0] = (float) pow(2, (round(getMidiNoteWithCents(getTrimmedMean(stack, 0.25)))-69)/12)*440;
  mRTTextSender2.PushData(mLastOutputData2);
  
}
#endif
