import threading
import queue
import time
import os
from gtts import gTTS
import pygame.mixer

class SpeechManager:
    def __init__(self, avatar_manager):
        self.avatar_manager = avatar_manager
        self.message_queue = queue.Queue()
        self.is_speaking = False
        pygame.mixer.init()  # Initialize mixer once

    def _tts_worker(self, text):
        """Worker thread for TTS processing"""
        try:
            # Generate speech
            tts = gTTS(text=text, lang="en")
            temp_file = f"tts_{time.time()}.mp3"
            tts.save(temp_file)
            
            # Play audio
            sound = pygame.mixer.Sound(temp_file)
            sound.play()
            self.is_speaking = True
            
            # Wait for playback to complete
            while pygame.mixer.get_busy():
                time.sleep(0.05)  # Shorter sleep for more responsiveness
            
        except Exception as e:
            print(f"Speech error: {e}")
        finally:
            if os.path.exists(temp_file):
                os.remove(temp_file)
            self.is_speaking = False

    def process_message(self, text):
        """Process a text message with TTS and animation"""
        if self.is_speaking:
            return  # Skip if already speaking
            
        
        threading.Thread(
            target=self._tts_worker,
            args=(text,),
            daemon=True
        ).start()

    def process_queue(self):
        """Process all messages in the queue"""
        if not self.is_speaking and not self.message_queue.empty():
            self.process_message(self.message_queue.get())