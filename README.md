# EarthTechProject - EcoThrow

EcoThrow is an educational 2D game developed in Python using Pygame. The player must sort waste by throwing it into the correct bins while taking into account physical factors like wind and gravity.

## Gameplay

You control a piece of waste and must aim, set your power, and throw it into the appropriate recycling bin.

### Objective
- Sort the waste correctly (Plastic, Paper, Glass).
- Reach the required score for each level to progress to the next.
- Preserve your lives until the end of the game.

### Challenges
- Wind: Influences the horizontal trajectory of your throw.
- Gravity: Varies by level and affects how fast the waste drops.
- The Shark Obstacle: A moving shark appears in the Ocean level. Touching it makes your waste bounce off.
- Wrong Bin: Throwing waste into the wrong recycling bin results in a loss of life.

### Controls
- ENTER: Start the game from the main menu.
- UP / DOWN Arrows: Adjust the throwing angle.
- LEFT / RIGHT Arrows: Adjust the throwing power.
- SPACE: Throw the waste.
- R: Restart the game from the end screens.

## Features
- Physics System: Projectile paths are influenced by gravity and wind over time.
- Trajectory Preview: A dotted aim guide is displayed before your throw based on physics calculations.
- Different Environments: Unique scenery including gradients for Beach, Forest, and Ocean levels.
- Immersive Game Feel: Bouncing UI elements, screen shakes, particle gravity, and satisfying retro sound effects.
- Dynamic Difficulty: Obstacles like animals and exams, plus moving recycling bins in later levels.
- Transparent UI: Interface elements with a frosted glass effect and a circular power gauge.
- English Codebase: Source code and comments are documented in English.

## Levels

| Level | Name | Setting | Mechanics |
|---|---|---|---|
| 1 | Beach | Sunny | No wind, standard gravity. |
| 2 | Forest | Cloudy | Introduction to wind mechanics. |
| 3 | Ocean | Underwater | Strong wind, higher gravity, and the shark obstacle. |
| 4 | Mountain | Snowy Peaks | Variable wind, high gravity, moving bins, and the eagle obstacle. |
| 5 | Antarctica | Ice & Igloos | Extreme wind, high gravity, moving bins, and the penguin obstacle. |
| 6 | Bonus Level | Campus | Intense wind, fast-moving bins, and a special flying exam obstacle. |

## Types of Waste & Bins
1. Plastic: Yellow Bin.
2. Paper: Blue Bin.
3. Glass: Green Bin.

## Project Structure

```text
EarthTechProject/
│
├── main.py       # Main game loop, graphics, visuals, UI, and event handling
├── physics.py    # Physics rules (velocity, positioning) and collision math
├── config.py     # Constants, colors palettes, and game parameters
└── README.md     # Project documentation
```

## Installation & Running

1. Install Python (version 3+ recommended).
2. Install Pygame (the main graphics library):
   ```bash
   pip install pygame
   ```
3. Start the game:
   ```bash
   python main.py
   ```

## Work Share
This project was developed equally by:
- Jonas Tubiana
- Jean Monier-Vinard Azoulay
- Nuri Ozyer
