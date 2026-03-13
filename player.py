# player.py — Player sprite with physics, animations & power-up states

import pygame
from settings import (
    PLAYER_W, PLAYER_H, PLAYER_X, GROUND_Y,
    GRAVITY, JUMP_STRENGTH,
    SHIELD_DURATION, DOUBLE_JUMP_DURATION,
    C_PLAYER, C_PLAYER_SHIELD, C_WHITE,
)
from utils import load_image, load_sound


class Player(pygame.sprite.Sprite):
    """
    The player character.

    States
    ------
    - Running on the ground (is_jumping = False)
    - First jump
    - Double jump (if double_jump power-up is active)
    - Shield active (survives one collision)

    Animation
    ---------
    The player cycles through frames stored in self.frames[state].
    If no image assets are found, a coloured rectangle is used instead.
    """

    ANIM_SPEED = 6          # frames per animation tick

    def __init__(self):
        super().__init__()

        # ── Load / build animation frames ─────────────────────
        self.frames = self._load_frames()
        self.anim_state  = "run"
        self.anim_index  = 0
        self.anim_timer  = 0

        self.image = self.frames[self.anim_state][0]
        self.rect  = self.image.get_rect(
            bottomleft=(PLAYER_X, GROUND_Y)
        )

        # ── Physics ───────────────────────────────────────────
        self.vel_y       = 0
        self.is_jumping  = False
        self.jumps_left  = 1          # increases to 2 with double-jump power-up

        # ── Power-up timers (ms, 0 = inactive) ────────────────
        self.shield_timer      = 0
        self.double_jump_timer = 0
        self.has_shield        = False
        self.has_double_jump   = False

        # ── Sounds ────────────────────────────────────────────
        self.sfx_jump = load_sound("assets/sounds/jump.wav")

    # ── Private helpers ───────────────────────────────────────

    def _load_frames(self) -> dict:
        """
        Try to load sprite-sheet frames from assets/images/.
        Falls back to a solid-colour surface if files are missing.
        """
        def placeholder(color):
            surf = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
            pygame.draw.rect(surf, color, surf.get_rect(), border_radius=10)
            # simple face so it feels alive
            eye_color = (255, 255, 255)
            pygame.draw.circle(surf, eye_color, (20, 28), 7)
            pygame.draw.circle(surf, eye_color, (40, 28), 7)
            pygame.draw.circle(surf, (30, 30, 30), (22, 28), 3)
            pygame.draw.circle(surf, (30, 30, 30), (42, 28), 3)
            return surf

        run_color  = C_PLAYER
        jump_color = (80, 180, 255)
        shield_col = C_PLAYER_SHIELD

        # Two slightly different run frames (legs shift)
        run1 = placeholder(run_color)
        run2 = placeholder(run_color)
        pygame.draw.rect(run2, (30, 100, 180), pygame.Rect(10, 60, 15, 20), border_radius=4)
        pygame.draw.rect(run2, (30, 100, 180), pygame.Rect(35, 55, 15, 20), border_radius=4)

        jump_frame    = placeholder(jump_color)
        shield_frame  = placeholder(shield_col)

        # Attempt real asset loading (images named run_0.png, run_1.png, jump_0.png)
        real_run = []
        for i in range(4):
            path = f"assets/images/player_run_{i}.png"
            img = load_image(path, (PLAYER_W, PLAYER_H))
            # load_image returns magenta placeholder if missing — keep the
            # built-in placeholder instead (it looks better than solid magenta)
            is_placeholder = (img.get_at((0, 0))[:3] == (220, 0, 220))
            if not is_placeholder:
                real_run.append(img)

        run_frames = real_run if len(real_run) == 4 else [run1, run2, run1, run2]

        real_jump = load_image("assets/images/player_jump_0.png", (PLAYER_W, PLAYER_H))
        jump_frames = [real_jump] if real_jump.get_at((0,0))[:3] != (220,0,220) else [jump_frame]

        return {
            "run":    run_frames,
            "jump":   jump_frames,
            "shield": [shield_frame],
        }

    # ── Public API ────────────────────────────────────────────

    def jump(self):
        """Attempt a jump (or double-jump if power-up is active)."""
        if self.jumps_left > 0:
            self.vel_y      = JUMP_STRENGTH
            self.is_jumping = True
            self.jumps_left -= 1
            self.anim_state = "jump"
            if self.sfx_jump:
                self.sfx_jump.play()

    def activate_shield(self):
        self.has_shield   = True
        self.shield_timer = SHIELD_DURATION

    def activate_double_jump(self):
        self.has_double_jump   = True
        self.double_jump_timer = DOUBLE_JUMP_DURATION
        self.jumps_left        = 2

    def absorb_hit(self) -> bool:
        """
        Called on collision.  Returns True if the player survives
        (shield absorbed the hit), False if game over.
        """
        if self.has_shield:
            self.has_shield   = False
            self.shield_timer = 0
            return True          # survived
        return False             # game over

    # ── Update ────────────────────────────────────────────────

    def update(self, dt: int):
        """dt = milliseconds since last frame (from Clock.tick)"""
        self._update_powerups(dt)
        self._apply_physics()
        self._advance_animation()

    def _update_powerups(self, dt: int):
        if self.shield_timer > 0:
            self.shield_timer -= dt
            if self.shield_timer <= 0:
                self.has_shield = False

        if self.double_jump_timer > 0:
            self.double_jump_timer -= dt
            if self.double_jump_timer <= 0:
                self.has_double_jump = False
                if self.jumps_left > 1:
                    self.jumps_left = 1

    def _apply_physics(self):
        self.vel_y     += GRAVITY
        self.rect.y    += int(self.vel_y)

        if self.rect.bottom >= GROUND_Y:
            self.rect.bottom = GROUND_Y
            self.vel_y       = 0
            self.is_jumping  = False
            self.anim_state  = "shield" if self.has_shield else "run"
            # restore jump count when landing
            self.jumps_left  = 2 if self.has_double_jump else 1

    def _advance_animation(self):
        frames = self.frames[self.anim_state]
        self.anim_timer += 1
        if self.anim_timer >= self.ANIM_SPEED:
            self.anim_timer  = 0
            self.anim_index += 1
            
        self.anim_index %= len(frames)
        self.image = frames[self.anim_index]

    # ── Draw ──────────────────────────────────────────────────

    def draw(self, surface):
        surface.blit(self.image, self.rect)

        # Shield glow ring
        if self.has_shield:
            cx = self.rect.centerx
            cy = self.rect.centery
            r  = max(self.rect.width, self.rect.height) // 2 + 8
            pygame.draw.circle(surface, C_PLAYER_SHIELD, (cx, cy), r, 3)

        # Double-jump indicator (small arc above head)
        if self.has_double_jump and self.jumps_left == 2:
            pygame.draw.arc(
                surface, (255, 220, 80),
                pygame.Rect(self.rect.x - 4, self.rect.top - 18, self.rect.width + 8, 20),
                0, 3.14, 3
            )