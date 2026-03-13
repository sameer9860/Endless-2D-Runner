# utils.py — Shared helper functions

import pygame
import os
from settings import HIGHSCORE_FILE, C_TEXT, C_TEXT_DIM, C_WHITE


# ── Font helpers ──────────────────────────────────────────────

def load_font(size: int, bold: bool = False) -> pygame.font.Font:
    """Return a SysFont monospace font at the given size."""
    return pygame.font.SysFont("monospace", size, bold=bold)


def draw_text(surface, text: str, font, color, center):
    """Blit text centred at the given (x, y) position."""
    surf = font.render(text, True, color)
    rect = surf.get_rect(center=center)
    surface.blit(surf, rect)


def draw_text_left(surface, text: str, font, color, topleft):
    """Blit text anchored to the top-left corner."""
    surf = font.render(text, True, color)
    surface.blit(surf, topleft)


# ── Asset loaders ─────────────────────────────────────────────

def load_image(path: str, size=None, alpha=True) -> pygame.Surface:
    """
    Load an image from *path*.  If the file doesn't exist a solid
    coloured placeholder rectangle is returned so the game still runs
    without an assets folder.
    """
    if os.path.exists(path):
        img = pygame.image.load(path)
        img = img.convert_alpha() if alpha else img.convert()
    else:
        # Placeholder: bright magenta so missing assets are obvious
        w, h = size if size else (64, 64)
        img = pygame.Surface((w, h), pygame.SRCALPHA if alpha else 0)
        img.fill((220, 0, 220))

    if size:
        img = pygame.transform.scale(img, size)
    return img


def load_sound(path: str) -> pygame.mixer.Sound | None:
    """Load a sound effect; return None (silently) if file is missing."""
    if os.path.exists(path):
        try:
            return pygame.mixer.Sound(path)
        except Exception:
            pass
    return None


def load_music(path: str) -> bool:
    """Queue a music file; returns True on success."""
    if os.path.exists(path):
        try:
            pygame.mixer.music.load(path)
            return True
        except Exception:
            pass
    return False


# ── High-score persistence ────────────────────────────────────

def read_highscore() -> int:
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            return int(f.read().strip())
    except Exception:
        return 0


def write_highscore(score: int) -> None:
    try:
        with open(HIGHSCORE_FILE, "w") as f:
            f.write(str(score))
    except Exception:
        pass


# ── Overlay helpers ───────────────────────────────────────────

def draw_overlay(surface, alpha: int = 160):
    """Draw a semi-transparent black rectangle over the whole screen."""
    overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, alpha))
    surface.blit(overlay, (0, 0))


# ── Simple button ─────────────────────────────────────────────

class Button:
    """
    A clickable text button drawn as a rounded rectangle.

    Usage
    -----
    btn = Button("Start", font, center=(450, 260))
    # inside draw loop:
    btn.draw(screen)
    # inside event loop:
    if btn.is_clicked(event):
        ...
    """

    PAD_X = 32
    PAD_Y = 14

    def __init__(self, label: str, font,
                 center: tuple,
                 color_idle=(50, 50, 75),
                 color_hover=(70, 70, 110),
                 text_color=C_WHITE,
                 border_color=(100, 100, 140)):
        self.label = label
        self.font  = font
        self.color_idle   = color_idle
        self.color_hover  = color_hover
        self.text_color   = text_color
        self.border_color = border_color

        surf = font.render(label, True, text_color)
        w = surf.get_width()  + self.PAD_X * 2
        h = surf.get_height() + self.PAD_Y * 2
        self.rect = pygame.Rect(0, 0, w, h)
        self.rect.center = center

    def draw(self, surface):
        mouse = pygame.mouse.get_pos()
        hovered = self.rect.collidepoint(mouse)
        color = self.color_hover if hovered else self.color_idle
        pygame.draw.rect(surface, color, self.rect, border_radius=8)
        pygame.draw.rect(surface, self.border_color, self.rect, 2, border_radius=8)
        draw_text(surface, self.label, self.font, self.text_color, self.rect.center)

    def is_clicked(self, event) -> bool:
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))