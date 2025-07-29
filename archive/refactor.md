Refactor by creating the following classes:


A class for the character Animation

```python
CharacterAnimation:
    def __init__(self, asset_name,  playback_speed):
        self.name = name
        self.front_frames = load_seq(f"assets/{asset_name}/front/{asset_name}")
        self.back_frames = load_seq(f"assets/{asset_name}/back/{asset_name}")
        self.left_frames = load_seq(f"assets/{asset_name}/left/{asset_name}")
        self.right_frames = load_seq(f"assets/{asset_name}/right/{asset_name}")
        
        self.playback_speed = playback_speed

    
```


```python
AvatarManager:
    def __init__(self):
        states = {
            'talking': CharacterAnimation('talking', 0.1),
            'idle': CharacterAnimation('idle', 0.1),
        }
    
    def set_to_state(self, state):
        for face...
    
    def draw_rotated...

```


And als tere is a SPeech manager of it 




