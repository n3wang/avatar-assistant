import threading
import queue
import time
import os
from gtts import gTTS
import pygame.mixer


class SpeechManager:
    """
    message_queue      ← 由外部(Flask)压入整段文本  
    process_queue()    ← 在 pygame 主循环里持续调用  
    speak()            ← 内部使用，把文本拆块并并行生成 MP3
    """

    def __init__(self, avatar_manager=None, chunk_size: int = 10):
        # 外部接口
        self.message_queue: "queue.Queue[str]" = queue.Queue()

        # 播放流水线
        self.avatar_manager = avatar_manager
        self.chunk_size = chunk_size
        self._ready_mp3 = {}               # {idx: path} 等待播放
        self._ready_lock = threading.Lock()
        self._next_play_idx = 0            # 下一个必须播放的 idx
        self._total_chunks = 0             # 当前 speak() 的总块数
        self._generated_cnt = 0            # 已生成的块计数
        self._generating = False           # 是否仍在生成 mp3

        pygame.mixer.init()

    # ────────────────────────── 公开属性与方法 ──────────────────────────
    @property
    def is_speaking(self) -> bool:
        """当前是否正在播放语音 (用于驱动动画)"""
        return pygame.mixer.get_busy()

    def process_queue(self):
        """
        必须在主循环里高频调用  
        • 如果正在播 -> 直接返回  
        • 如果上一段播完 -> 清理文件  
        • 若下一个 MP3 已就绪 -> 立即播放  
        • 若播放管线空闲并且有新消息 -> start speak()
        """
        # 1) 正在播
        if self.is_speaking:
            return

        # 2) 播放完毕 → 删除上一块文件
        finished_idx = self._next_play_idx - 1
        if finished_idx >= 0:
            old_path = f"tts_{finished_idx}.mp3"
            if os.path.exists(old_path):
                os.remove(old_path)

        # 3) 如果有下一块已准备好 → 播
        with self._ready_lock:
            path = self._ready_mp3.pop(self._next_play_idx, None)

        if path:
            pygame.mixer.Sound(path).play()
            self._next_play_idx += 1
            return                     # 播放启动，返回等待下一帧

        # 4) 没有下一块且生成已完成 → 管线空闲
        pipeline_idle = (
            not self._generating and
            not self._ready_mp3 and
            not self.is_speaking
        )
        if pipeline_idle and not self.message_queue.empty():
            # 从主消息队列取出新的整段文本开始 speak
            self.speak(self.message_queue.get())

    # ────────────────────────── 内部实现 ──────────────────────────
    def speak(self, text: str):
        """把整段文本切块、并行生成 MP3，并重置播放管线"""
        # 拆块
        words = text.split()
        chunks = [
            " ".join(words[i:i + self.chunk_size])
            for i in range(0, len(words), self.chunk_size)
        ]

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
        """后台线程：生成单个 MP3 并放入缓冲区"""
        try:
            path = f"tts_{idx}.mp3"
            gTTS(text=text, lang="es", tld="us").save(path)
            with self._ready_lock:
                self._ready_mp3[idx] = path
        except Exception as e:
            print(f"[TTS ERROR] {e}")
        finally:
            # 更新生成计数；若全部完成则标记 _generating False
            with self._ready_lock:
                self._generated_cnt += 1
                if self._generated_cnt >= self._total_chunks:
                    self._generating = False


# ──────────────────────────────── quick demo ──
if __name__ == "__main__":
    sm = SpeechManager(chunk_size=10)
    msg = (
        "Este es un mensaje muy largo que debe ser dividido "
        "automáticamente en partes de diez palabras para ser procesado "
        "correctamente por el sistema de síntesis de voz."
    )
    sm.speak(msg)

    # keep main thread alive until playback thread ends
    while sm.playback_thread.is_alive():
        time.sleep(0.1)
