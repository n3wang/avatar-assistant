import pygame
import sys
import websockets
import asyncio
import threading
from gtts import gTTS
import time
import os

# Initialize pygame
pygame.init()

# Set up the display
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("WebSocket Controlled Square")

# Colors
DEFAULT_COLOR = (255, 0, 0)    # Red
REACT_COLOR = (0, 0, 255)      # Blue
WHITE = (255, 255, 255)

# Square properties
square_size = 100
square_x = width // 2 - square_size // 2
square_y = height // 2 - square_size // 2
current_color = DEFAULT_COLOR

# WebSocket
ws_url = "ws://127.0.0.1:8000/ws/avatar"

# Lock for safely updating shared state
color_lock = threading.Lock()

def speak_and_reset(text):
    global current_color

    try:
        # Generate speech
        tts = gTTS(text=text, lang='en', slow=False)
        audio_file = "temp_speech.mp3"
        tts.save(audio_file)

        # Play audio
        pygame.mixer.init()
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()

        # Wait until playback finishes
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)

        # Reset color
        with color_lock:
            current_color = DEFAULT_COLOR

        # Clean up
        os.remove(audio_file)

    except Exception as e:
        print(f"Speech error: {e}")
        with color_lock:
            current_color = DEFAULT_COLOR

def handle_message(action, text_to_speak):
    global current_color
    print(f"Received action: {action} | Text: {text_to_speak}")
    if action == "react":
        with color_lock:
            current_color = REACT_COLOR
        threading.Thread(target=speak_and_reset, args=(text_to_speak,), daemon=True).start()

async def websocket_listener():
    async with websockets.connect(ws_url) as websocket:
        while True:
            try:
                message = await websocket.recv()
                if "::" in message:
                    action, speech = message.split("::", 1)
                    handle_message(action.strip(), speech.strip())
            except websockets.exceptions.ConnectionClosed:
                print("WebSocket connection closed")
                break

def start_websocket_loop():
    asyncio.run(websocket_listener())

# Start WebSocket in background
ws_thread = threading.Thread(target=start_websocket_loop, daemon=True)
ws_thread.start()

# Button properties
button_rect = pygame.Rect(width // 2 - 50, height // 2 + 100, 100, 40)
button_color = (70, 130, 180)
button_text = "Trigger"

# Font setup
font = pygame.font.SysFont('Arial', 20)

# Main loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if button_rect.collidepoint(event.pos):
                print("Trigger button clicked")

    # Fill background
    screen.fill(WHITE)

    # Draw square
    with color_lock:
        pygame.draw.rect(screen, current_color, (square_x, square_y, square_size, square_size))

    # Draw button
    pygame.draw.rect(screen, button_color, button_rect)
    text_surface = font.render(button_text, True, WHITE)
    text_rect = text_surface.get_rect(center=button_rect.center)
    screen.blit(text_surface, text_rect)

    pygame.display.flip()

pygame.quit()
sys.exit()
