# Pitch Control 
### (A pitch detection and shifting plugin)
## CS Project 2020-21 (3rd Year 40-credit module)

A VST plugin providing a chromatic tuner and simple pitch shifting features.

This project uses the iPlug2 framework to create end products in a variety of audio plugin formats (including Audio Unit (AU) and VST3). As a consequence, a large part of the code in this repository is taken from the open-source [iPlug2 repository](https://github.com/iplug2/iplug2) - the license for which is included again in this repository as [/iPlug2License](/PitchControl/iPlug2LICENSE.txt). Since most of the code remains unchanged, it is the following files which make up the main part of this project (these are the files which are predominantly my own work - some basic boilerplate code remains as written by the iPlug2 authors): 

- [PitchControl.c](PitchControl/PitchControl.c) - (PitchControl/PitchControl.c)
- [PitchControl.h](PitchControl/PitchControl.h) - (PitchControl/PitchControl.h)
- fft.c (yet to be included)

## How To Use the Output Audio Plugins

Although Pitch Control software is available as a standalone application, it's main use is intended as an audio plugin for a Digital Audio Workstation (DAW). The end product audio plugins (contained in [OutputAudioPlugins](/OutputAudioPlugins)) will work on any system which has a DAW on it (so long as that DAW accepts plugins of the form VST and/or AU). One such free Digital Audio Workstation (DAW) is [Audacity](https://www.audacityteam.org/) which will accept plugins of the form VST - as will the DAW [Reaper](https://www.reaper.fm/) which has a free 60 day trial. I personally use [Logic Pro X](https://www.apple.com/uk/logic-pro/) which doesn't accept VSTs but instead uses Audio Units (AUs), though testing has been done on a variety of DAWs.
The standalone app will use the computer's audio input to run pitch detection and pitch shifting on, whilst the plugins will be used inside a DAW to act on a chosen audio singal. 

## How To Compile
Although end users will only need the actual plugin ( the .vst or .component file) and none of the other files in this repository, it may be of interest to explain how you would compile the project using the [PitchControl](PitchControl) folder. 
In order to compile the code it is first necessary to install the iPlug2 framework (along with Xcode for MacOS or Visual Studio Community for Windows) and then copy the [PitchControl](PitchControl) folder into the 'Projects' folder located in iPlug2/Projects. Then opening the [Xcode workspace](PitchControl/PitchControl.xcworkspace) or [Visual Studio solutions file](PitchControl/PitchControl.sln) it is possible to compile the PitchControl plugin (it may be useful here to refer to the tutorial given in the iPlug2 [wiki]() ([MacOS Tutorial](https://github.com/iPlug2/iPlug2/wiki/01_Getting_started_mac_ios), [Windows Tutorial](https://github.com/iPlug2/iPlug2/wiki/01_Getting_started_mac_ios))
