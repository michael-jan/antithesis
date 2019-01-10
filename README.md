# Antithesis
This repository houses Antithesis, my investigation into the reverse-engineering of synthesized sounds using machine learning techniques. Feel free to explore my code!

### Introduction
Electronic music producers use synthesizers to craft sounds that we hear in modern music. Being able to hear a sound and recreate it on a synthesizer is a hard task that generally takes a music producer years of experience to master. It follows that an algorithmic method to "re-create" the parameters from raw audio would be invaluable to music producers. For one, producers can study how said sounds were created and become better sound designers. Furthermore, they could make edits to existing sounds and samples to use in their music.

Perhaps modern machine learning techniques can be used to "hear" such sounds and predict the parameters (the "preset") that created it in a given synth.

### Methodology
I started by generating a dataset of audio-preset pairs by randomly setting the parameters in a synth and subsequently rendering the audio. This process was automated with a script I automated in Python using [pyautogui](https://github.com/asweigart/pyautogui). The VST synth plugin I chose for my experiments was [Mika Micro](https://tesselode.itch.io/mika-micro), due to it being a lightweight open-source subtractive synth. To facilitate the saving and loading of presets from Mika Micro in raw text format (as opposed to the humanly-unreadable .fxp format), I modified its C++ code and rebuilt the plugin from Visual Studio.

<img align="right" width="200" height="150" src="https://i.stack.imgur.com/pXIap.png">

To preprocess the audio files, I experimented with generating spectrograms and mel-spectrograms of different sizes with the help of [Kapre](https://github.com/keunwoochoi/kapre). Spectrograms, such as the one to the right, have become a popular audio preprocessing tool because they represent audio in the frequency-domain rather than the time-domain—and indoingso convert the signal into an image-like form. Thus, image-processing techniques can now be performed. Thus, once the audio was in this image-like format, I fed it into a convolutional neural network implemented in [Keras](https://keras.io/).

### Results
The results were mixed but promising. My convolutional neural network was able to correctly predict values such as attach and decay, but had trouble predicting more nuanced parameters such as the "oscillator split." Oftentimes in the world of sound synthesis, sound designers may split a single oscillator into two or more signals—effectively detuning just enough so that the human ear still only hears a single fundamental frequency, but with a "widening" effect. Perhaps this slight detuning was lost when the signal was binned into different frequency bands during its spectrogram conversion.

Another caveat is that there are multiple ways of designing very similar sounds—which makes this problem fundamentally different from other regression/classification problems. For example, an image of a piece of clothing cannot be correctly labeled as both "blue pants" and "red shirt." However, in the world of sound design, the same sound may be created 
