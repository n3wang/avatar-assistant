import pygame
import sys
import threading
import queue
import time
import os
from flask import Flask, request, jsonify
from gtts import gTTS
import pygame.mixer

# === Pygame Setup ===
pygame.init()
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Pygame + Flask")

# Colors
WHITE = (255, 255, 255)
REACT_COLOR = (0, 0, 255)
DEFAULT_COLOR = (255, 0, 0)
current_color = DEFAULT_COLOR
square_size = 100
square_x = width // 2 - square_size // 2
square_y = height // 2 - square_size // 2



message_queue = queue.Queue()
color_lock = threading.Lock()
app = Flask(__name__)

@app.route("/post-message", methods=["POST"])
def post_message():
    data = request.get_json()
    if not data or "text" not in data:
        return jsonify({"error": "Missing 'text'"}), 400

    message_queue.put(data["text"])
    return jsonify({"status": "Message received"}), 200

def run_flask():
    app.run(port=5000)

def speak_and_reset(text):
    global current_color
    try:
        
        tts = gTTS(text=text, lang="en")
        tts.save("temp.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("temp.mp3")
        
        with color_lock:
            current_color = REACT_COLOR
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
        os.remove("temp.mp3")
    except Exception as e:
        print(f"Error: {e}")
    with color_lock:
        current_color = DEFAULT_COLOR

# === Start Flask Thread ===
flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()

running = True
font = pygame.font.SysFont("Arial", 20)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Check for messages
    while not message_queue.empty():
        message = message_queue.get()
        threading.Thread(target=speak_and_reset, args=(message,), daemon=True).start()

    screen.fill(WHITE)
    with color_lock:
        pygame.draw.rect(screen, current_color, (square_x, square_y, square_size, square_size))
    pygame.display.flip()

pygame.quit()
sys.exit()
