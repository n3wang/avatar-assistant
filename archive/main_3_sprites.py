import pygame, sys, threading, queue, time, os
from flask import Flask, request, jsonify
from gtts import gTTS
import pygame.mixer

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("3D Holographic Pyramid")

BACKGROUND = (0, 0, 0)          # dark blue

def load_seq(prefix: str, count: int):
    """Load a list of numbered PNGs:  prefix1.png … prefixN.png"""
    return [pygame.image.load(f"{prefix}{i+1}.png").convert_alpha() for i in range(count)]

def draw_rotated(img, pos, angle, size):
    img = pygame.transform.scale(img, size)
    img = pygame.transform.rotate(img, angle)
    rect = img.get_rect(center=pos)
    screen.blit(img, rect)

# ------------------ sprites ------------------
try:
    # idle sequences
    idle_front  = load_seq("assets/idle/front/idle",   4)
    idle_back   = load_seq("assets/idle/back/idle",    4)
    idle_left   = load_seq("assets/idle/left/idle",    4)
    idle_right  = load_seq("assets/idle/right/idle",   4)
    # talking sequences
    talk_front  = load_seq("assets/talking/front/talking", 4)
    talk_back   = load_seq("assets/talking/back/talking",  4)
    talk_left   = load_seq("assets/talking/left/talking",  4)
    talk_right  = load_seq("assets/talking/right/talking", 4)
    
except Exception as e:
    print("❌ Image-load error:", e); sys.exit(1)

faces = [
    dict(name="front",  idle=idle_front,  talk=talk_front,
         pos=(WIDTH//2, 100),         ang=  0, size=(200,200), talking=False),
    dict(name="back",   idle=idle_back,   talk=talk_back,
         pos=(WIDTH//2, HEIGHT-100),     ang=180, size=(200,200), talking=False),
    dict(name="left",   idle=idle_left,   talk=talk_left,
         pos=(100,      HEIGHT//2),      ang= 90, size=(200,200), talking=False),
    dict(name="right",  idle=idle_right,  talk=talk_right,
         pos=(WIDTH-100, HEIGHT//2),     ang=-90, size=(200,200), talking=False),
]

app = Flask(__name__)
msg_q: queue.Queue[str] = queue.Queue()

@app.route("/post-message", methods=["POST"])
def post_msg():
    data = request.get_json(silent=True) or {}
    text = data.get("text")
    if not text:
        return jsonify(error="Missing 'text'"), 400
    msg_q.put(text)
    return jsonify(status="queued")

def run_flask():          # thread target
    app.run(port=5000)

threading.Thread(target=run_flask, daemon=True).start()

def speak_and_animate(text: str):
    """Background thread: play TTS and flag talking state."""
    try:
        # mark talking
        
        # create / play audio
        tts = gTTS(text=text, lang="en")
        tts.save("tmp.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load("tmp.mp3")
        pygame.mixer.music.play()
        for f in faces: f["talking"] = True
        # wait for playback to finish
        while pygame.mixer.music.get_busy():
            time.sleep(0.1)
    except Exception as e:
        print("❌ Speech error:", e)
    finally:
        pygame.mixer.quit()
        if os.path.exists("tmp.mp3"): os.remove("tmp.mp3")
        for f in faces: f["talking"] = False   # back to idle

# ===================== Main loop =====================
clock          = pygame.time.Clock()
frame_idle     = 0
frame_talk     = 0
IDLE_SPEED     = 100     # bigger → slower
TALK_SPEED     = 5

running = True
while running:
    # ----- events -----
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT: running = False

    # ----- new messages -----
    while not msg_q.empty():
        threading.Thread(target=speak_and_animate,
                         args=(msg_q.get(),), daemon=True).start()

    # ----- update frames -----
    if any(f["talking"] for f in faces):
        if pygame.time.get_ticks() // (1000//TALK_SPEED) != frame_talk:
            frame_talk = (frame_talk + 1) % len(talk_front)
    else:
        if pygame.time.get_ticks() // (1000//IDLE_SPEED) != frame_idle:
            frame_idle = (frame_idle + 1) % len(idle_front)

    # ----- draw -----
    screen.fill(BACKGROUND)
    for f in faces:
        seq = f["talk"] if f["talking"] else f["idle"]
        idx = frame_talk if f["talking"] else frame_idle
        draw_rotated(seq[idx % len(seq)], f["pos"], f["ang"], f["size"])
    pygame.display.flip()
    clock.tick(10)

pygame.quit()
sys.exit()
