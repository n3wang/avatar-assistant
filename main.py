import pygame
import sys
import argparse
import multiprocessing
from multiprocessing import Process, Queue, Value
from avatar_manager import AvatarManager
from speech_manager import SpeechManager
from web_server import create_web_server
from constants import WIDTH, HEIGHT


def run_second_window(state_queue, stop_event):
    """Run the second window in a separate process"""
    pygame.init()
    pygame_icon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(pygame_icon)

    # Create a smaller window for front-facing view
    second_width = WIDTH // 2
    second_height = HEIGHT // 2
    screen = pygame.display.set_mode((second_width, second_height))
    pygame.display.set_caption("3D Holographic Avatar - Front View")

    # Create avatar manager for front view only
    avatar_manager = AvatarManager(character_name="clerk", frames_count=10, scale=1.0,
                                   is_front_only=True, speed_talking=70, speed_idle=100)

    clock = pygame.time.Clock()
    is_speaking = False

    while not stop_event.is_set():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                stop_event.set()
                return

        # Get state from main process
        while not state_queue.empty():
            try:
                is_speaking = state_queue.get_nowait()
            except:
                pass

        # Update and draw
        avatar_manager.update(is_speaking)
        screen.fill((0, 0, 0))
        avatar_manager.draw_front_centered(screen, is_speaking, second_width, second_height)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()


def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='3D Holographic Avatar')
    parser.add_argument('--second-window', action='store_true',
                        help='Enable second window with front-facing avatar')
    args = parser.parse_args()

    # Initialize pygame
    pygame.init()
    pygame_icon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(pygame_icon)

    # Create main window with 4 avatars
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Holographic Avatar - Main")

    # Setup second window process if flag is set
    second_window_process = None
    state_queue = None
    stop_event = None

    if args.second_window:
        state_queue = Queue()
        stop_event = multiprocessing.Event()
        second_window_process = Process(target=run_second_window, args=(state_queue, stop_event))
        second_window_process.start()

    # Create managers
    avatar_manager = AvatarManager(character_name="clerk", frames_count=10, scale=.7,
                                   is_front_only=False, speed_talking=70, speed_idle=100)

    speech_manager = SpeechManager(avatar_manager)
    create_web_server(speech_manager)

    # Main game loop
    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        speech_manager.process_queue()
        avatar_manager.update(speech_manager.is_speaking)

        # Share speaking state with second window
        if args.second_window and state_queue is not None:
            try:
                state_queue.put_nowait(speech_manager.is_speaking)
            except:
                pass  # Queue full, skip this update

        # Render main window
        screen.fill((0, 0, 0))
        avatar_manager.draw(screen, speech_manager.is_speaking)
        pygame.display.flip()

        clock.tick(60)

    # Cleanup second window
    if second_window_process:
        stop_event.set()
        second_window_process.join(timeout=2)
        if second_window_process.is_alive():
            second_window_process.terminate()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()