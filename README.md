# AutomaticSpeechRecognition
Python GUI application for AutomaticSpeechRecognition




# Automatic Speech Recognition with Audio Analysis

## Overview

This project is a PyQt5-based application that provides automatic speech recognition (ASR) and audio analysis features. It allows users to record or upload an audio file, transcribe the speech content using a speech recognition API, and analyze various properties of the audio, including duration, sample rate, and waveform visualization.

## Features

- **Record Audio**: Capture audio directly through the application.
- **Upload Audio**: Upload an existing audio file for analysis and transcription.
- **Play Audio**: Play back the recorded or uploaded audio.
- **Transcription**: Convert speech from the audio file into text using a speech recognition API.
- **Audio Analysis**: Analyze the audio to display properties like duration, sample rate, number of channels, and more.
- **Waveform Visualization**: Visualize the audio waveform using `matplotlib` and display it in the application.
- **Export Audio Analysis**: Save the audio analysis results to a text file.
- **Save Transcription**: Save the transcribed text to a file for later use.
- **Clear Results**: Reset the application state and clear all displayed results.

## Installation

### Prerequisites

- Python 3.x
- PyQt5
- NumPy
- SciPy
- Matplotlib
- Requests

### Clone the Repository

```bash
git clone https://github.com/Sherin-SEF-AI/AutomaticSpeechRecognition.git

cd AutomaticSpeechRecognition

Install Dependencies

You can install the required Python libraries using pip:


pip install PyQt5 numpy scipy matplotlib requests
Usage
Running the Application

To start the application, navigate to the project directory and run the following command:

How to Use
Record Audio: Click the "Record Audio" button to start recording. Click again to stop recording.
Upload Audio: Click the "Upload Audio" button to select an existing audio file for analysis.
Play Audio: Click the "Play Audio" button to listen to the recorded or uploaded audio.
Analyze Audio: Click the "Analyze Audio" button to view the audio's properties and visualize the waveform.
Export Analysis: Click the "Export Analysis" button to save the audio analysis results to a text file.
Save Transcription: Click the "Save Transcription" button to save the transcribed text to a file.
Clear Results: Click the "Clear Results" button to reset the application and clear all data.
