import threading
import queue
import time
import os
from gtts import gTTS
import pygame.mixer
from pydub import AudioSegment


class SpeechManager:
    """
    message_queue      ← 由外部(Flask)压入整段文本  
    process_queue()    ← 在 pygame 主循环里持续调用  
    speak()            ← 内部使用，把文本拆块并并行生成 MP3
    """

    def __init__(self, avatar_manager=None, chunk_size: int = 10):
        self.message_queue: "queue.Queue[str]" = queue.Queue()

        self.avatar_manager = avatar_manager
        self.chunk_size = chunk_size
        self._ready_mp3 = {}               
        self._ready_lock = threading.Lock()
        self._next_play_idx = 0            
        self._total_chunks = 0             
        self._generated_cnt = 0            
        self._generating = False           

        pygame.mixer.init()

    @property
    def is_speaking(self) -> bool:
        return pygame.mixer.get_busy()

    def process_queue(self):
        if self.is_speaking:
            return

        finished_idx = self._next_play_idx - 1
        if finished_idx >= 0:
            old_path = f"tts_{finished_idx}.mp3"
            if os.path.exists(old_path):
                os.remove(old_path)

        with self._ready_lock:
            path = self._ready_mp3.pop(self._next_play_idx, None)

        if path:
            pygame.mixer.Sound(path).play()
            self._next_play_idx += 1
            return

        pipeline_idle = (
            not self._generating and
            not self._ready_mp3 and
            not self.is_speaking
        )
        if pipeline_idle and not self.message_queue.empty():
            self.speak(self.message_queue.get())

    def speak(self, text: str):
        """把整段文本切块、并行生成 MP3，并重置播放管线"""
        # 拆块
        words = text.split()
        chunks = []
        i = 0
        size = self.chunk_size
        while i < len(words):
            chunk = " ".join(words[i:i + size])
            chunks.append(chunk)
            i += size
            size *= 3  # Exponential growth
        

        # 重置流水线
        self._ready_mp3.clear()
        self._next_play_idx = 0
        self._total_chunks = len(chunks)
        self._generated_cnt = 0
        self._generating = True

        # 并行生成
        for idx, chunk in enumerate(chunks):
            threading.Thread(
                target=self._tts_worker,
                args=(idx, chunk),
                daemon=True,
            ).start()

    def _tts_worker(self, idx: int, text: str):
        try:
            temp_path = f"temp_tts_{idx}.mp3"
            path = f"tts_{idx}.mp3"
            gTTS(text=text, lang="en", tld="us").save(temp_path)
            speed_to_use = 1.3 + min(.6, .2*idx)
            
            audio = AudioSegment.from_file(temp_path, format="mp3")
            
            # print({
            #     'i': idx,
            #     'duration' : audio.duration_seconds,
            #     'sample_rate' : audio.frame_rate,
            #     'channels' : audio.channels,
            #     'sample_width' : audio.sample_width,
            #     'frame_count' : audio.frame_count(),
            #     'frame_rate' : audio.frame_rate,
            #     'frame_width' : audio.frame_width,
            # })

            final = audio.speedup(playback_speed=speed_to_use)

            # print({
            #     'i': idx,
            #     'modified duration' : final.duration_seconds,
            #     'sample_rate' : final.frame_rate,
            #     'channels' : final.channels,
            #     'sample_width' : final.sample_width,
            #     'frame_count' : final.frame_count(),
            #     'frame_rate' : final.frame_rate,
            #     'frame_width' : final.frame_width,
            #     'speed': speed_to_use
            # })
            final.export(path, format="mp3")
            with self._ready_lock:
                self._ready_mp3[idx] = path
                
        except Exception as e:
            print(f"[TTS ERROR] {e}")
        finally:
            with self._ready_lock:
                self._generated_cnt += 1
                if self._generated_cnt >= self._total_chunks:
                    self._generating = False


if __name__ == "__main__":
    sm = SpeechManager(chunk_size=5)
    msg = (
        "Este es un mensaje muy largo que debe ser dividido "
        "automáticamente en partes de diez palabras para ser procesado "
        "correctamente por el sistema de síntesis de voz."
    )
    sm.speak(msg)

    # keep main thread alive until playback thread ends
    while sm.playback_thread.is_alive():
        time.sleep(0.1)
