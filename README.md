# Key Climber

A 2D platformer game built with Pygame Zero.

## Description

Key Climber is a classic platformer where you control a character navigating through platforms, avoiding enemies, and collecting keys to reach the exit door. The game features smooth sprite animations, multiple enemy types, and a complete menu system.

## Features

- **Platformer Gameplay**: Jump and move through platforms with physics-based controls
- **Enemy AI**: Multiple enemy types with patrol behavior
- **Sprite Animation**: Animated characters both when moving and idle
- **Menu System**: Clickable buttons for game start, audio controls, and exit
- **Audio**: Background music and sound effects
- **Lives System**: Three lives with game over screen
- **Win Condition**: Find the key and reach the door

## Requirements

- Python 3.8 or higher
- Pygame Zero

## Installation

1. Install Pygame Zero:
```bash
pip install pgzero
```

2. Run the game:
```bash
python KeyClimber.py
```

## Controls

- **Arrow Keys**: Move left/right
- **Space**: Jump
- **ESC**: Return to menu (during gameplay)
- **Mouse**: Click menu buttons

## Game Rules

1. Collect the yellow key
2. Avoid enemies (bee, mouse, slimes)
3. Reach the door to win
4. Don't fall off the map
5. You have 3 lives

## Project Structure

```
Key Climber/
├── KeyClimber.py          # Main game file
├── terrain_map.csv        # Level map data
├── images/                # Sprites and graphics
├── music/                 # Background music
└── sounds/                # Sound effects
```

## Technical Details

- **Engine**: Pygame Zero
- **Language**: Python
- **Code Lines**: ~390 lines
- **Classes**: Player, Enemy, Item, Button
- **Physics**: Custom gravity and collision detection

## Author

**Made by EduarrdoVS**

## License

This project was created for educational purposes.