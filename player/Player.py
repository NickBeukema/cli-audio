"""PyAudio Example: Play a wave file (callback version)."""

import pyaudio
import wave
import time
from error.CliAudioFileException import CliAudioFileException

class Player:
    def __init__(self):
        self.currentSong = "Nothing playing."
        self.paused = True
        self.position = 0
        self.stream = None

    def getCurrentSong(self):
        return self.currentSong

    def pause(self):
        if self.paused == False:
            self.paused = True
            self.stream.stop_stream()
        else:
            self.paused = False
            self.stream.start_stream()

    def play(self, track):
        self.paused = False
        self.currentSong = track

        try:
            self.wf = wave.open(track, 'rb')

            # instantiate PyAudio (1)
            self.p = pyaudio.PyAudio()

            # open self.stream using callback (3)
            self.stream = self.p.open(format=self.p.get_format_from_width(self.wf.getsampwidth()),
                    channels=self.wf.getnchannels(),
                    rate=self.wf.getframerate(),
                    output=True,
                    stream_callback=self.callback)

            # start the self.stream (4)
            self.stream.start_stream()

        except (FileNotFoundError, wave.Error):
            raise CliAudioFileException


    def stop(self):
        if self.stream is None:
            return

        self.stream.stop_stream()
        self.stream.close()
        self.wf.close()

        self.p.terminate() 

    def callback(self, in_data, frame_count, time_info, status):
        data = self.wf.readframes(frame_count)
        return (data, pyaudio.paContinue)

