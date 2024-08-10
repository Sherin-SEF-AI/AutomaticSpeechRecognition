import sys
import requests
import json
import pyaudio
import wave
import numpy as np
from scipy.io import wavfile
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel, QTextEdit, QFileDialog, QHBoxLayout, QProgressBar, QStatusBar, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QPixmap
import os
import matplotlib.pyplot as plt

class RecordingThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, audio_path, record_seconds, chunk, sample_format, channels, rate):
        super().__init__()
        self.audio_path = audio_path
        self.record_seconds = record_seconds
        self.chunk = chunk
        self.sample_format = sample_format
        self.channels = channels
        self.rate = rate
        self.running = True

    def run(self):
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=self.sample_format, channels=self.channels,
                            rate=self.rate, frames_per_buffer=self.chunk,
                            input=True)

            frames = []
            total_chunks = int(self.rate / self.chunk * self.record_seconds)
            
            for i in range(total_chunks):
                if not self.running:
                    break
                data = stream.read(self.chunk, exception_on_overflow=False)
                frames.append(data)
                progress = (i / total_chunks) * 100
                if i % 10 == 0:  # Update progress less frequently to reduce GUI load
                    self.progress.emit(int(progress))
            
            stream.stop_stream()
            stream.close()
            p.terminate()

            with wave.open(self.audio_path, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(p.get_sample_size(self.sample_format))
                wf.setframerate(self.rate)
                wf.writeframes(b''.join(frames))

            self.finished.emit(self.audio_path)
        except Exception as e:
            self.error.emit(str(e))

    def stop(self):
        self.running = False
        self.wait()

class SpeechRecognitionApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Speech Recognition App with Audio Analysis")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout(self.central_widget)

        self.label = QLabel("Record or upload an audio file for speech recognition:")
        self.layout.addWidget(self.label)

        self.button_layout = QHBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.record_button = QPushButton("Record Audio")
        self.record_button.clicked.connect(self.toggle_recording)
        self.button_layout.addWidget(self.record_button)

        self.upload_button = QPushButton("Upload Audio")
        self.upload_button.clicked.connect(self.upload_audio)
        self.button_layout.addWidget(self.upload_button)

        self.play_button = QPushButton("Play Audio")
        self.play_button.clicked.connect(self.play_audio)
        self.button_layout.addWidget(self.play_button)

        self.analyze_button = QPushButton("Analyze Audio")
        self.analyze_button.clicked.connect(self.analyze_audio)
        self.button_layout.addWidget(self.analyze_button)

        self.export_analysis_button = QPushButton("Export Analysis")
        self.export_analysis_button.clicked.connect(self.export_audio_analysis)
        self.button_layout.addWidget(self.export_analysis_button)

        self.save_button = QPushButton("Save Transcription")
        self.save_button.clicked.connect(self.save_transcription)
        self.button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton("Clear Results")
        self.clear_button.clicked.connect(self.clear_results)
        self.button_layout.addWidget(self.clear_button)

        self.progress_bar = QProgressBar()
        self.layout.addWidget(self.progress_bar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        self.result_text = QTextEdit()
        self.result_text.setReadOnly(True)
        self.layout.addWidget(self.result_text)

        self.graphics_view = QGraphicsView()
        self.scene = QGraphicsScene(self.graphics_view)
        self.graphics_view.setScene(self.scene)
        self.layout.addWidget(self.graphics_view)

        self.audio_path = None
        self.transcription = None
        self.recording = False
        self.recording_thread = None
        self.audio_analysis = {}

        # Audio settings
        self.chunk = 1024
        self.sample_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 44100
        self.record_seconds = 300

    def toggle_recording(self):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        self.recording = True
        self.record_button.setText("Stop Recording")
        self.result_text.setText("Recording...")
        self.audio_path = "recorded_audio.wav"
        self.progress_bar.setValue(0)

        # Start the recording thread
        self.recording_thread = RecordingThread(
            audio_path=self.audio_path,
            record_seconds=self.record_seconds,
            chunk=self.chunk,
            sample_format=self.sample_format,
            channels=self.channels,
            rate=self.rate
        )
        self.recording_thread.progress.connect(self.update_progress_bar)
        self.recording_thread.finished.connect(self.on_recording_finished)
        self.recording_thread.error.connect(self.on_recording_error)
        self.recording_thread.start()

    def stop_recording(self):
        if self.recording_thread:
            self.recording_thread.stop()
        self.recording = False
        self.record_button.setText("Record Audio")

    def update_progress_bar(self, progress):
        self.progress_bar.setValue(progress)

    def on_recording_finished(self, audio_path):
        self.result_text.setText("Recording finished. Uploading...")
        self.upload_audio(audio_path)

    def on_recording_error(self, error_message):
        self.result_text.setText(f"Error during recording: {error_message}")
        self.recording = False
        self.record_button.setText("Record Audio")

    def upload_audio(self, audio_path=None):
        if not audio_path and not self.audio_path:
            self.result_text.setText("No audio file available!")
            return

        url = "https://chatgpt-42.p.rapidapi.com/whisperv3"
        headers = {
            "x-rapidapi-key": "2d7198105fmsha78df4c828aea6ep182ce4jsn6a513052a904",
            "x-rapidapi-host": "chatgpt-42.p.rapidapi.com",
        }

        with open(audio_path or self.audio_path, 'rb') as audio_file:
            files = {'file': audio_file}
            response = requests.post(url, files=files, headers=headers)

        if response.status_code == 200:
            result = response.json()
            self.transcription = result.get('text', 'No transcription available.')
            self.result_text.setText(f"Transcription: {self.transcription}")
        else:
            self.result_text.setText(f"Failed to upload audio. Status code: {response.status_code}")

    def play_audio(self):
        if not self.audio_path or not os.path.exists(self.audio_path):
            self.result_text.setText("No audio file to play!")
            return

        chunk = 1024
        wf = wave.open(self.audio_path, 'rb')
        p = pyaudio.PyAudio()

        stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                        channels=wf.getnchannels(),
                        rate=wf.getframerate(),
                        output=True)

        data = wf.readframes(chunk)
        while data:
            stream.write(data)
            data = wf.readframes(chunk)

        stream.stop_stream()
        stream.close()
        p.terminate()
        self.result_text.setText("Playback complete.")

    def analyze_audio(self):
        if not self.audio_path or not os.path.exists(self.audio_path):
            self.result_text.setText("No audio file to analyze!")
            return

        try:
            rate, data = wavfile.read(self.audio_path)
            self.audio_analysis = {
                "Duration": len(data) / rate,
                "Sample Rate": rate,
                "Channels": data.shape[1] if len(data.shape) > 1 else 1,
                "Total Samples": len(data),
            }
            self.result_text.setText(f"Audio Analysis:\n"
                                     f"Duration: {self.audio_analysis['Duration']} seconds\n"
                                     f"Sample Rate: {self.audio_analysis['Sample Rate']} Hz\n"
                                     f"Channels: {self.audio_analysis['Channels']}\n"
                                     f"Total Samples: {self.audio_analysis['Total Samples']}")
            self.plot_waveform(data, rate)
        except Exception as e:
            self.result_text.setText(f"Error analyzing audio: {str(e)}")

    def plot_waveform(self, data, rate):
        self.scene.clear()
        plt.figure(figsize=(10, 3))
        if data.ndim == 1:
            plt.plot(np.linspace(0, len(data) / rate, num=len(data)), data)
        else:
            plt.plot(np.linspace(0, len(data) / rate, num=len(data)), data[:, 0])
        plt.xlabel("Time [s]")
        plt.ylabel("Amplitude")
        plt.title("Audio Waveform")
        plt.grid(True)

        plt.savefig("waveform.png")
        plt.close()

        pixmap = QPixmap("waveform.png")
        self.scene.addItem(QGraphicsPixmapItem(pixmap))
        os.remove("waveform.png")

    def export_audio_analysis(self):
        if not self.audio_analysis:
            self.result_text.setText("No audio analysis available to export!")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Audio Analysis", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            with open(file_path, 'w') as file:
                for key, value in self.audio_analysis.items():
                    file.write(f"{key}: {value}\n")
            self.result_text.setText(f"Audio analysis saved to {file_path}.")

    def save_transcription(self):
        if not self.transcription:
            self.result_text.setText("No transcription available to save!")
            return

        options = QFileDialog.Options()
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Transcription", "", "Text Files (*.txt);;All Files (*)", options=options)

        if file_path:
            with open(file_path, 'w') as file:
                file.write(self.transcription)
            self.result_text.setText(f"Transcription saved to {file_path}.")

    def clear_results(self):
        self.result_text.clear()
        self.audio_path = None
        self.transcription = None
        self.progress_bar.setValue(0)
        self.record_button.setText("Record Audio")
        self.scene.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    mainWin = SpeechRecognitionApp()
    mainWin.show()
    sys.exit(app.exec_())

