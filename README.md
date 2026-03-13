# Endless 2D Runner — Setup & Asset Guide

## Quick Start
```
pip install pygame
python main.py
```

## Controls
| Key | Action |
|-----|--------|
| SPACE / ↑ | Jump (double-jump with 2↑ power-up) |
| ESC | Pause |

## File Structure
```
Endless-2D-Runner/
├── main.py          ← game loop, screens, orchestration
├── player.py        ← Player class (physics, animation, power-ups)
├── obstacle.py      ← Obstacle, Coin, PowerUp classes
├── settings.py      ← all tunable constants
├── utils.py         ← fonts, buttons, asset loaders, high-score I/O
├── highscore.txt    ← auto-created on first game-over
└── assets/
    ├── images/
    │   ├── player_run_0.png   (60×80 px) ← optional sprite frames
    │   ├── player_run_1.png
    │   ├── player_run_2.png
    │   ├── player_run_3.png
    │   ├── player_jump_0.png
    │   ├── obs_spike.png      (30×80 px)
    │   ├── obs_block.png      (55×45 px)
    │   ├── obs_cactus.png     (40×65 px)
    │   └── coin.png           (28×28 px)
    ├── sounds/
    │   ├── jump.wav
    │   ├── hit.wav
    │   ├── coin.wav
    │   ├── milestone.wav
    │   ├── powerup.wav
    │   └── music.ogg          ← background music loop
    └── fonts/                 ← (optional custom TTF fonts)
```

> **All assets are optional.**  The game runs fine with built-in
> placeholder graphics and silent audio if the files are absent.

## Tuning
All gameplay values live in **settings.py**:

| Constant | Effect |
|---|---|
| `GRAVITY` | How fast the player falls |
| `JUMP_STRENGTH` | How high the player jumps (negative = up) |
| `OBS_BASE_SPEED` | Starting obstacle speed |
| `OBS_SPEED_CAP` | Maximum speed the game scales to |
| `OBS_BASE_INTERVAL` | Starting ms between obstacle spawns |
| `OBS_MIN_INTERVAL` | Fastest spawn rate allowed |
| `SHIELD_DURATION` | How long a shield lasts (ms) |
| `DOUBLE_JUMP_DURATION` | How long double-jump lasts (ms) |
| `COIN_VALUE` | Points per coin collected |
| `MILESTONE_INTERVAL` | Play milestone sound every N points |

## Step-by-step build order
Each step below maps to a specific part of the code:

| Step | Feature | Files touched |
|------|---------|--------------|
| 2 | Game loop + window | `main.py` — `Game.run()`, `Game._draw()` |
| 3 | Player jump & gravity | `player.py` — `Player._apply_physics()` |
| 4 | Obstacles & collision | `obstacle.py` — `Obstacle`, `main.py` — `Game._update()` |
| 5 | Score & difficulty | `main.py` — score tracking, `settings.py` speed constants |
| 6 | Scrolling background | `main.py` — `Background`, `ParallaxLayer` |
| 7 | Sprites & animation | `player.py` — `_load_frames()`, `_advance_animation()` |
| 8 | Sound & music | `main.py` — `SoundManager` |
| 9 | Menus & pause & game-over | `main.py` — `MenuScreen`, `PauseScreen`, `GameOverScreen` |
| 10 | Coins, power-ups, high score | `obstacle.py` — `Coin`, `PowerUp`; `utils.py` — `read/write_highscore` |