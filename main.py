import pygame
import sys
from avatar_manager import AvatarManager
from speech_manager import SpeechManager
from web_server import create_web_server
from constants import WIDTH, HEIGHT

def main():
    # Initialize pygame
    pygame.init()
    pygame_icon = pygame.image.load('assets/icon.png')
    pygame.display.set_icon(pygame_icon)
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Holographic Avatar")
    
    # Create managers
    # avatar_manager = AvatarManager()
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
        screen.fill((0, 0, 0))
        avatar_manager.draw(screen, speech_manager.is_speaking)
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()