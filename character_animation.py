import sys
import pygame

class CharacterAnimation:
    def __init__(self, asset_name, playback_speed, frame_count=4, scale=1.0, character_name="", is_front_only=True):
        """Initialize animation sequences for all directions"""
        self.asset_name = asset_name
        self.playback_speed = playback_speed
        self.frame_count = frame_count
        self.character_name = character_name
        self.scale = scale
        self.current_frame = 0
        self.last_update = 0
        
        if is_front_only:
            self.front = self._load_sequence("front")
            self.back = self._load_sequence("front")
            self.left = self._load_sequence("front")
            self.right = self._load_sequence("front")
        else:
            self.front = self._load_sequence("front")
            self.back = self._load_sequence("back")
            self.left = self._load_sequence("left")
            self.right = self._load_sequence("right")
    
    def _load_sequence(self, direction):
        """Load and scale animation frames for a direction"""
        frames = []
        for i in range(self.frame_count):
            try:
                assets_path = f"assets/{self.asset_name}/{direction}/{self.asset_name}{i+1}.png"
                if self.character_name:
                    assets_path = f"assets/{self.character_name}/{self.asset_name}/{direction}/{self.asset_name}{i+1}.png"
                img = pygame.image.load(
                    assets_path
                ).convert_alpha()
                if self.scale != 1.0:
                    size = (int(img.get_width() * self.scale), 
                            int(img.get_height() * self.scale))
                    img = pygame.transform.scale(img, size)
                frames.append(img)
            except Exception as e:
                print(f"Error loading {direction} frame {i}: {e}")
                sys.exit(1)
        return frames
    
    def update(self):
        """Update animation frame based on playback speed"""
        now = pygame.time.get_ticks()
        if now - self.last_update > self.playback_speed:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.last_update = now
    
    def get_frame(self, direction):
        """Get current frame for specified direction"""
        return {
            "front": self.front,
            "back": self.back,
            "left": self.left,
            "right": self.right
        }[direction][self.current_frame]