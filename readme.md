## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Ensure you have the required assets in the `assets/` directory

## Usage

### Basic Usage (Single Window - 4 Avatars)

Run the application with all 4 avatar views in one window:

```bash
python main.py
```

### Dual Window Mode (4 Avatars + Front View)

Run the application with a second window showing only the front-facing avatar:

```bash
python main.py --second-window
```

### Command Line Parameters

- `--second-window`: Enable a second window with a centered front-facing avatar view
  - The second window runs in a separate process
  - Both windows are synchronized and show the same avatar talking in sync
  - The second window is half the size of the main window (900x500)

## API Usage

The application exposes a web server on port 5001 for sending messages to the avatar.

### Endpoint

**POST** `/post-message`

### Request Format

**Headers:**
```
Content-Type: application/json
```

**Body:**
```json
{
  "text": "Your message here"
}
```

### Examples

#### Using cURL

```bash
curl -X POST http://localhost:5001/post-message \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello, I am your virtual assistant!"}'
```


## Configuration

Edit `main.py` to customize the avatar:

```python
avatar_manager = AvatarManager(
    character_name="clerk",  # Character asset folder name
    frames_count=10,         # Number of animation frames
    scale=0.7,              # Avatar scale
    is_front_only=False,    # Use all 4 directions
    speed_talking=70,       # Animation speed when talking (ms)
    speed_idle=100          # Animation speed when idle (ms)
)
```
