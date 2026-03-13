# settings.py — All game constants in one place

# ── Screen ────────────────────────────────────────────────────
SCREEN_WIDTH  = 900
SCREEN_HEIGHT = 500
FPS           = 60
TITLE         = "Endless Runner"

# ── World ─────────────────────────────────────────────────────
GROUND_Y      = SCREEN_HEIGHT - 60   # y-coordinate of ground surface
GRAVITY       = 0.85
JUMP_STRENGTH = -19

# ── Player ────────────────────────────────────────────────────
PLAYER_W      = 60
PLAYER_H      = 80
PLAYER_X      = 120                  # fixed horizontal position

# ── Obstacles ─────────────────────────────────────────────────
OBS_BASE_SPEED    = 6.0
OBS_BASE_INTERVAL = 1800             # ms between spawns
OBS_MIN_INTERVAL  = 700
OBS_SPEED_CAP     = 18.0

# ── Scoring ───────────────────────────────────────────────────
SCORE_PER_OBS      = 1
MILESTONE_INTERVAL = 10              # every N points → play milestone sound
HIGHSCORE_FILE     = "highscore.txt"

# ── Coins / Power-ups ─────────────────────────────────────────
COIN_SPEED         = OBS_BASE_SPEED
COIN_VALUE         = 5
SHIELD_DURATION    = 5000            # ms
DOUBLE_JUMP_DURATION = 8000          # ms

# ── Parallax scroll speeds (bg layers) ────────────────────────
LAYER_SPEEDS = [1.0, 2.5, 5.0]      # far → near

# ── Colors ───────────────────────────────────────────────────
C_BG          = (15,  15,  25)
C_GROUND      = (40,  40,  60)
C_GROUND_LINE = (60,  60,  90)
C_PLAYER      = (52,  152, 219)
C_PLAYER_SHIELD = (52, 219, 200)
C_OBS         = (231, 76,  60)
C_OBS2        = (155, 89,  182)
C_COIN        = (241, 196, 15)
C_TEXT        = (220, 220, 235)
C_TEXT_DIM    = (120, 120, 150)
C_ACCENT      = (46,  204, 113)
C_DANGER      = (231, 76,  60)
C_WHITE       = (255, 255, 255)
C_BLACK       = (0,   0,   0)