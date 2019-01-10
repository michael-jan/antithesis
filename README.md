# Antithesis
This repository houses Antithesis, my investigation into the reverse-engineering of synthesized sounds using machine learning.

### Introduction
Electronic music producers use synthesizers to craft sounds that we hear in modern music. Being able to hear a sound and recreate it on a synthesizer is a hard task that generally takes a music producer years of experience to master. Perhaps modern machine learning techniques can be used to "hear" such sounds and predict the parameters (the "preset") that created it in a given synth.

### Methodology:
I started by generating a dataset of audio-preset pairs by randomly setting the parameters in a synth and subsequently rendering the audio. This process was automated with a script I automated in Python using [pyautogui](https://github.com/asweigart/pyautogui). The synth I chose for my experiements was [Mika Micro](https://tesselode.itch.io/mika-micro), due to it being a lightweight open-source subtractive synth.
To preprocess the audio files, I experimented with generating spectrograms and mel-spectrograms of different sizes with the help of [Kapre](https://github.com/keunwoochoi/kapre)

