#pragma once

#include "IPlug_include_in_plug_hdr.h"
#include "IControls.h"

const int kNumPresets = 1;

enum EParams
{
  kGain = 0,
  kNumParams
};
enum EControlTags
{
  kCtrlTagRTText,
  kCtrlTagRTText2
};

using namespace iplug;
using namespace igraphics;

class PitchControl final : public Plugin
{
public:
  PitchControl(const InstanceInfo& info);

#if IPLUG_DSP // http://bit.ly/2S64BDd
public:
  void ProcessBlock(sample** inputs, sample** outputs, int nFrames) override;
  void OnIdle() override;
private:
  ISender<1> mRTTextSender;
  ISenderData<1> mLastOutputData = { kCtrlTagRTText, 1, 0 };
  ISender<1> mRTTextSender2;
  ISenderData<1> mLastOutputData2 = { kCtrlTagRTText2, 1, 0 };
#endif
};
