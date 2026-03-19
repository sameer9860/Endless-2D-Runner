# obstacle.py — Obstacles and collectible Coins

import pygame
import random
from settings import (
    SCREEN_WIDTH, GROUND_Y,
    C_OBS, C_OBS2, C_COIN,
)
from utils import load_image, load_sound


# ── Obstacle ──────────────────────────────────────────────────

class Obstacle(pygame.sprite.Sprite):
    """
    An obstacle that scrolls from right to left.

    Three visual varieties are picked at random:
      0 — tall thin spike   (red)
      1 — short wide block  (purple)
      2 — medium cactus     (green)
    """

    VARIETIES = [
        {"w": 30, "h": 80, "color": C_OBS,          "image": "assets/images/obs_spike.png", "type": "ground"},
        {"w": 55, "h": 45, "color": C_OBS2,          "image": "assets/images/obs_block.png", "type": "ground"},
        {"w": 40, "h": 65, "color": (46, 139, 87),   "image": "assets/images/obs_cactus.png", "type": "ground"},
        {"w": 45, "h": 40, "color": (200, 50, 200),  "image": "assets/images/obs_fly.png", "type": "high"},
    ]

    def __init__(self, speed: float):
        super().__init__()
        variety = random.choice(self.VARIETIES)

        w, h = variety["w"], variety["h"]
        self.speed = speed

        # Try loading a real image; fall back to a coloured rectangle
        img = load_image(variety["image"], (w, h))
        if img.get_at((0, 0))[:3] == (220, 0, 220):   # magenta = placeholder
            img = self._make_shape(variety["color"], w, h)

        self.image = img
        if variety.get("type") == "high":
            self.rect  = self.image.get_rect(bottomleft=(SCREEN_WIDTH + 10, GROUND_Y - 50))
        else:
            self.rect  = self.image.get_rect(bottomleft=(SCREEN_WIDTH + 10, GROUND_Y))

        # Slightly smaller hit-box for fairness
        self.hitbox = self.rect.inflate(-10, -6)

    def _make_shape(self, color, w, h) -> pygame.Surface:
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=5)
        # simple highlight stripe
        pygame.draw.rect(surf, tuple(min(c + 50, 255) for c in color),
                         pygame.Rect(4, 4, w - 8, 8), border_radius=3)
        return surf

    def update(self, *args, **kwargs):
        self.rect.x   -= int(self.speed)
        self.hitbox.x  = self.rect.x + 5    # keep hitbox in sync

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @property
    def off_screen(self) -> bool:
        return self.rect.right < 0

    @property
    def passed_player(self) -> bool:
        """True once the obstacle has scrolled past the player's x position."""
        from settings import PLAYER_X, PLAYER_W
        return self.rect.right < PLAYER_X


# ── Coin ──────────────────────────────────────────────────────

class Coin(pygame.sprite.Sprite):
    """
    A collectible coin that floats at a random height above the ground.
    Collecting it gives COIN_VALUE points.
    """

    RADIUS  = 14
    COLORS  = [(241, 196, 15), (243, 156, 18)]   # gold / orange-gold
    BOB_AMP = 5       # pixels of vertical bobbing
    BOB_SPD = 0.08    # radians per frame

    def __init__(self, speed: float):
        super().__init__()
        self.speed = speed
        self._angle = random.uniform(0, 6.28)

        # Vertical position: somewhere in the upper two-thirds of jump height
        low_y  = GROUND_Y - 40
        high_y = GROUND_Y - 140
        self._base_y = random.randint(high_y, low_y)

        # Build coin image
        img = load_image("assets/images/coin.png", (self.RADIUS * 2, self.RADIUS * 2))
        if img.get_at((0, 0))[:3] == (220, 0, 220):
            img = self._make_coin()
        self.image = img

        self.rect = self.image.get_rect(
            center=(SCREEN_WIDTH + 20, self._base_y)
        )

    def _make_coin(self) -> pygame.Surface:
        r   = self.RADIUS
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, self.COLORS[0], (r, r), r)
        pygame.draw.circle(surf, self.COLORS[1], (r, r), r, 2)
        # shine dot
        pygame.draw.circle(surf, (255, 240, 120), (r - 4, r - 4), 4)
        return surf

    def update(self, *args, **kwargs):
        self._angle     += self.BOB_SPD
        import math
        self.rect.x     -= int(self.speed)
        self.rect.centery = int(self._base_y + math.sin(self._angle) * self.BOB_AMP)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @property
    def off_screen(self) -> bool:
        return self.rect.right < 0


# ── Power-up pickup ───────────────────────────────────────────

class PowerUp(pygame.sprite.Sprite):
    """
    A floating icon representing either a shield or double-jump boost.
    kind ∈ {"shield", "double_jump"}
    """

    KIND_COLORS = {
        "shield":      (52,  219, 200),
        "double_jump": (255, 220, 80),
    }
    KIND_LABELS = {
        "shield":      "S",
        "double_jump": "2↑",
    }

    def __init__(self, speed: float, kind: str = None):
        super().__init__()
        self.speed = speed
        self.kind  = kind or random.choice(["shield", "double_jump"])
        color      = self.KIND_COLORS[self.kind]
        label      = self.KIND_LABELS[self.kind]

        self.image = self._make_icon(color, label)
        self.rect  = self.image.get_rect(
            center=(SCREEN_WIDTH + 20, GROUND_Y - 110)
        )

    def _make_icon(self, color, label) -> pygame.Surface:
        size = 36
        surf = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, surf.get_rect(), border_radius=8)
        pygame.draw.rect(surf, (255, 255, 255), surf.get_rect(), 2, border_radius=8)
        fnt  = pygame.font.SysFont("monospace", 14, bold=True)
        txt  = fnt.render(label, True, (0, 0, 0))
        surf.blit(txt, txt.get_rect(center=(size // 2, size // 2)))
        return surf

    def update(self, *args, **kwargs):
        self.rect.x -= int(self.speed)

    def draw(self, surface):
        surface.blit(self.image, self.rect)

    @property
    def off_screen(self) -> bool:
        return self.rect.right < 0