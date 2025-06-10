import pygame
import sys
from avatar_manager import AvatarManager
from speech_manager import SpeechManager
from web_server import create_web_server
from constants import WIDTH, HEIGHT

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("3D Holographic Avatar")
    
    # Create managers
    avatar_manager = AvatarManager()
    speech_manager = SpeechManager(avatar_manager)
    create_web_server(speech_manager)
    
    # Main game loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Process incoming messages
        speech_manager.process_queue()
        
        # Update and draw
        avatar_manager.update(speech_manager.is_speaking)
        screen.fill((0, 0, 0))
        avatar_manager.draw(screen, speech_manager.is_speaking)
        
        pygame.display.flip()
        clock.tick(60)  # Consistent 60 FPS
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()