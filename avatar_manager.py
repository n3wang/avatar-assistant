import pygame
from character_animation import CharacterAnimation
from constants import WIDTH, HEIGHT, FROM_CENTER

class AvatarManager:
    def __init__(self):
        self.states = {
            'talking': CharacterAnimation('talking', 50, scale=0.5),
            'idle': CharacterAnimation('idle', 100, scale=0.5),
        }
        self.current_state = 'idle'
        
        # Calculate center and positions
        width=WIDTH
        height=HEIGHT
        distance_from_center = FROM_CENTER
        self.center_x = width // 2
        self.center_y = height // 2
        self.distance = distance_from_center
        
        # Configure faces with dynamic positioning
        self.faces = self._configure_faces()

    def _configure_faces(self):
        """Generate face positions based on distance from center"""
        return [
            {
                "name": "front",
                "direction": "front",
                "pos": (self.center_x, self.center_y - self.distance),
                "angle": 0
            },
            {
                "name": "back",
                "direction": "back",
                "pos": (self.center_x, self.center_y + self.distance),
                "angle": 180
            },
            {
                "name": "left",
                "direction": "left",
                "pos": (self.center_x - self.distance, self.center_y),
                "angle": 90
            },
            {
                "name": "right",
                "direction": "right",
                "pos": (self.center_x + self.distance, self.center_y),
                "angle": -90
            }
        ]

    def set_state(self, state):
        """Set the current animation state"""
        if state not in self.states:
            raise ValueError(f"Invalid state: {state}")
        self.current_state = state

    def update(self, is_talking):
        """Update animations based on speaking state"""
        if is_talking:
            self.states['talking'].update()
        else:
            self.states['idle'].update()

    def draw(self, screen, is_talking):
        """Draw all faces"""
        state = 'talking' if is_talking else 'idle'
        for face in self.faces:
            frame = self.states[state].get_frame(face["direction"])
            self._draw_rotated(screen, frame, face["pos"], face["angle"])

    def _draw_rotated(self, screen, img, pos, angle):
        """Draw rotated image"""
        img = pygame.transform.rotate(img, angle)
        rect = img.get_rect(center=pos)
        screen.blit(img, rect)