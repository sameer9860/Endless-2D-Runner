
import sys
import math
import random
import pygame

from settings import *
from player   import Player
from obstacle import Obstacle, Coin, PowerUp
from utils    import (
    load_font, draw_text, draw_text_left,
    draw_overlay, Button,
    read_highscore, write_highscore,
    load_sound, load_music,
)


# ══════════════════════════════════════════════════════════════
#  BACKGROUND  (Step 6 — scrolling parallax)
# ══════════════════════════════════════════════════════════════

class ParallaxLayer:
    """One scrolling background strip (tiles horizontally)."""

    def __init__(self, color_top, color_bot, speed: float, y: int, h: int,
                 detail_color=None):
        self.speed       = speed
        self.y           = y
        self.h           = h
        self.color_top   = color_top
        self.color_bot   = color_bot
        self.detail_col  = detail_color
        self.x_offset    = 0.0

        # Build a tile that is 2× the screen width so we can scroll seamlessly
        self.tile_w = SCREEN_WIDTH * 2
        self.tile   = self._make_tile()

    def _make_tile(self) -> pygame.Surface:
        surf = pygame.Surface((self.tile_w, self.h))
        # gradient fill
        for row in range(self.h):
            t   = row / max(self.h - 1, 1)
            col = tuple(int(self.color_top[i] + (self.color_bot[i] - self.color_top[i]) * t)
                        for i in range(3))
            pygame.draw.line(surf, col, (0, row), (self.tile_w, row))
        # random star / cloud details
        if self.detail_col:
            rng = random.Random(id(self))
            for _ in range(80):
                x = rng.randint(0, self.tile_w - 1)
                y = rng.randint(0, self.h - 1)
                r = rng.randint(1, 3)
                pygame.draw.circle(surf, self.detail_col, (x, y), r)
        return surf

    def update(self):
        self.x_offset = (self.x_offset + self.speed) % self.tile_w

    def draw(self, surface):
        x = -self.x_offset
        while x < SCREEN_WIDTH:
            surface.blit(self.tile, (x, self.y))
            x += self.tile_w


class Background:
    """Three-layer parallax background + scrolling ground strip."""

    def __init__(self):
        # Sky
        self.layers = [
            ParallaxLayer((10, 10, 30),  (25, 25, 55),  LAYER_SPEEDS[0],
                          0, GROUND_Y, detail_color=(200, 200, 220)),
            # Mid hills
            ParallaxLayer((20, 20, 60),  (35, 35, 90),  LAYER_SPEEDS[1],
                          GROUND_Y - 80, 90, detail_color=None),
            # Near layer
            ParallaxLayer((30, 30, 80),  (45, 45, 100), LAYER_SPEEDS[2],
                          GROUND_Y - 30, 35, detail_color=None),
        ]
        self.ground_x = 0.0

    def update(self):
        for layer in self.layers:
            layer.update()
        self.ground_x = (self.ground_x + OBS_BASE_SPEED) % 40

    def draw(self, surface):
        for layer in self.layers:
            layer.draw(surface)

        # Ground strip
        pygame.draw.rect(surface, C_GROUND,
                         pygame.Rect(0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))
        # Ground dashes
        for x in range(0, SCREEN_WIDTH + 40, 40):
            rx = int(x - self.ground_x)
            pygame.draw.line(surface, C_GROUND_LINE,
                             (rx, GROUND_Y + 6), (rx + 20, GROUND_Y + 6), 2)


# ══════════════════════════════════════════════════════════════
#  HUD  (Step 5 + Step 9)
# ══════════════════════════════════════════════════════════════

class HUD:
    def __init__(self, fonts):
        self.fonts = fonts

    def draw(self, surface, score: int, highscore: int,
             speed: float, shield: bool, double_jump: bool):
        # Score
        draw_text_left(surface,
                       f"SCORE  {score:05d}",
                       self.fonts["sm"], C_TEXT, (20, 18))
        draw_text_left(surface,
                       f"BEST   {highscore:05d}",
                       self.fonts["sm"], C_TEXT_DIM, (20, 46))
        # Speed indicator
        bar_w = int((speed - OBS_BASE_SPEED) / (OBS_SPEED_CAP - OBS_BASE_SPEED) * 160)
        bar_w = max(0, min(bar_w, 160))
        pygame.draw.rect(surface, (40, 40, 60), pygame.Rect(SCREEN_WIDTH - 200, 18, 160, 14),
                         border_radius=4)
        if bar_w:
            pygame.draw.rect(surface, C_ACCENT,
                             pygame.Rect(SCREEN_WIDTH - 200, 18, bar_w, 14), border_radius=4)
        draw_text_left(surface, "SPD",
                       self.fonts["xs"], C_TEXT_DIM, (SCREEN_WIDTH - 228, 18))

        # Power-up icons
        ix = SCREEN_WIDTH - 200
        iy = 44
        if shield:
            self._draw_icon(surface, "SHD", C_PLAYER_SHIELD, ix, iy)
            ix += 60
        if double_jump:
            self._draw_icon(surface, "2↑", (255, 220, 80), ix, iy)

    def _draw_icon(self, surface, label, color, x, y):
        rect = pygame.Rect(x, y, 50, 22)
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, C_WHITE, rect, 1, border_radius=5)
        draw_text(surface, label, self.fonts["xs"], C_BLACK, rect.center)


# ══════════════════════════════════════════════════════════════
#  SCREENS  (Step 9)
# ══════════════════════════════════════════════════════════════

class MenuScreen:
    def __init__(self, fonts):
        self.fonts = fonts
        cx = SCREEN_WIDTH  // 2
        self.btn_start = Button("▶  START GAME",   fonts["med"], (cx, 260))
        self.btn_inst  = Button("?  HOW TO PLAY",  fonts["med"], (cx, 320))
        self.btn_quit  = Button("✕  QUIT",         fonts["med"], (cx, 380))
        self._show_instructions = False

    def handle_event(self, event) -> str:
        """Return 'play', 'quit', or '' """
        if self._show_instructions:
            if event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                self._show_instructions = False
            return ""
        if self.btn_start.is_clicked(event): return "play"
        if self.btn_quit.is_clicked(event):  return "quit"
        if self.btn_inst.is_clicked(event):
            self._show_instructions = True
        return ""

    def draw(self, surface, highscore: int):
        if self._show_instructions:
            self._draw_instructions(surface)
            return

        draw_overlay(surface, 180)
        draw_text(surface, "ENDLESS  RUNNER",
                  self.fonts["title"], C_ACCENT,
                  (SCREEN_WIDTH // 2, 150))
        draw_text(surface, f"Best: {highscore}",
                  self.fonts["sm"], C_TEXT_DIM,
                  (SCREEN_WIDTH // 2, 205))
        self.btn_start.draw(surface)
        self.btn_inst.draw(surface)
        self.btn_quit.draw(surface)
        draw_text(surface, "© press SPACE to jump",
                  self.fonts["xs"], C_TEXT_DIM,
                  (SCREEN_WIDTH // 2, SCREEN_HEIGHT - 24))

    def _draw_instructions(self, surface):
        draw_overlay(surface, 210)
        cx = SCREEN_WIDTH // 2
        lines = [
            ("HOW TO PLAY", self.fonts["med"], C_ACCENT, 140),
            ("SPACE / ↑  — Jump (hold for higher)", self.fonts["sm"], C_TEXT, 210),
            ("Double-jump with 2↑ power-up",        self.fonts["sm"], C_TEXT, 245),
            ("Collect  coins  for bonus points",     self.fonts["sm"], C_TEXT, 280),
            ("SHD  shield survives one hit",         self.fonts["sm"], C_TEXT, 315),
            ("Speed increases as your score climbs", self.fonts["sm"], C_TEXT_DIM, 365),
            ("[ click or press any key to go back ]",self.fonts["xs"], C_TEXT_DIM, 420),
        ]
        for text, font, color, y in lines:
            draw_text(surface, text, font, color, (cx, y))


class PauseScreen:
    def __init__(self, fonts):
        self.fonts = fonts
        cx = SCREEN_WIDTH // 2
        self.btn_resume = Button("▶  RESUME",   fonts["med"], (cx, 260))
        self.btn_quit   = Button("⏹  MAIN MENU", fonts["med"], (cx, 320))

    def handle_event(self, event) -> str:
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            return "resume"
        if self.btn_resume.is_clicked(event): return "resume"
        if self.btn_quit.is_clicked(event):   return "menu"
        return ""

    def draw(self, surface):
        draw_overlay(surface, 160)
        draw_text(surface, "PAUSED",
                  self.fonts["title"], C_TEXT,
                  (SCREEN_WIDTH // 2, 170))
        self.btn_resume.draw(surface)
        self.btn_quit.draw(surface)


class GameOverScreen:
    def __init__(self, fonts):
        self.fonts = fonts
        cx = SCREEN_WIDTH // 2
        self.btn_restart = Button("↺  PLAY AGAIN",  fonts["med"], (cx, 310))
        self.btn_menu    = Button("⌂  MAIN MENU",   fonts["med"], (cx, 370))

    def handle_event(self, event) -> str:
        if self.btn_restart.is_clicked(event): return "restart"
        if self.btn_menu.is_clicked(event):    return "menu"
        return ""

    def draw(self, surface, score: int, highscore: int, is_new_best: bool):
        draw_overlay(surface, 180)
        draw_text(surface, "GAME  OVER",
                  self.fonts["title"], C_DANGER,
                  (SCREEN_WIDTH // 2, 160))
        draw_text(surface, f"Score: {score}",
                  self.fonts["big"], C_TEXT,
                  (SCREEN_WIDTH // 2, 225))
        if is_new_best:
            draw_text(surface, "★ NEW HIGH SCORE ★",
                      self.fonts["med"], C_COIN,
                      (SCREEN_WIDTH // 2, 268))
        else:
            draw_text(surface, f"Best: {highscore}",
                      self.fonts["sm"], C_TEXT_DIM,
                      (SCREEN_WIDTH // 2, 268))
        self.btn_restart.draw(surface)
        self.btn_menu.draw(surface)


# ══════════════════════════════════════════════════════════════
#  SOUND MANAGER  (Step 8)
# ══════════════════════════════════════════════════════════════

class SoundManager:
    def __init__(self):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        self.sfx = {
            "jump":      load_sound("assets/sounds/jump.wav"),
            "hit":       load_sound("assets/sounds/hit.wav"),
            "coin":      load_sound("assets/sounds/coin.wav"),
            "milestone": load_sound("assets/sounds/milestone.wav"),
            "powerup":   load_sound("assets/sounds/powerup.wav"),
        }
        self._music_loaded = load_music("assets/sounds/music.ogg")
        self.music_playing = False

    def play(self, name: str):
        sfx = self.sfx.get(name)
        if sfx:
            sfx.play()

    def start_music(self):
        if self._music_loaded and not self.music_playing:
            pygame.mixer.music.play(-1)   # loop forever
            self.music_playing = True

    def stop_music(self):
        pygame.mixer.music.stop()
        self.music_playing = False

    def toggle_music(self):
        if self.music_playing:
            self.stop_music()
        else:
            self.start_music()


# ══════════════════════════════════════════════════════════════
#  GAME STATE  (Steps 2 – 10 wired together)
# ══════════════════════════════════════════════════════════════

class Game:

    STATE_MENU     = "menu"
    STATE_PLAYING  = "playing"
    STATE_PAUSED   = "paused"
    STATE_GAMEOVER = "gameover"

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock  = pygame.time.Clock()

        # Fonts
        self.fonts = {
            "title": load_font(52, bold=True),
            "big":   load_font(40, bold=True),
            "med":   load_font(26, bold=True),
            "sm":    load_font(20),
            "xs":    load_font(14),
        }

        # Sub-systems
        self.bg      = Background()
        self.sounds  = SoundManager()
        self.hud     = HUD(self.fonts)

        # Screens
        self.menu_screen     = MenuScreen(self.fonts)
        self.pause_screen    = PauseScreen(self.fonts)
        self.gameover_screen = GameOverScreen(self.fonts)

        # Persistent data
        self.highscore = read_highscore()

        self.state = self.STATE_MENU
        self._setup_game()

    # ── Setup / reset ─────────────────────────────────────────

    def _setup_game(self):
        """Reset all in-game state."""
        self.player   = Player()
        self.obstacles: list[Obstacle] = []
        self.coins:     list[Coin]     = []
        self.powerups:  list[PowerUp]  = []

        self.score      = 0
        self.last_milestone = 0
        self.speed      = OBS_BASE_SPEED
        self.spawn_interval = OBS_BASE_INTERVAL

        now = pygame.time.get_ticks()
        self.last_obs_spawn   = now
        self.last_coin_spawn  = now + 3000
        self.last_pup_spawn   = now + 8000
        self.is_new_best      = False

    # ── Main loop entry ───────────────────────────────────────

    def run(self):
        self.sounds.start_music()
        while True:
            dt = self.clock.tick(FPS)
            self._handle_events()
            self._update(dt)
            self._draw()

    # ── Event handling ────────────────────────────────────────

    def _handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit()

            # ── Menu ──────────────────────────────────────────
            if self.state == self.STATE_MENU:
                action = self.menu_screen.handle_event(event)
                if action == "play":
                    self._setup_game()
                    self.state = self.STATE_PLAYING
                elif action == "quit":
                    self._quit()

            # ── Playing ───────────────────────────────────────
            elif self.state == self.STATE_PLAYING:
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.player.jump()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = self.STATE_PAUSED

            # ── Paused ────────────────────────────────────────
            elif self.state == self.STATE_PAUSED:
                action = self.pause_screen.handle_event(event)
                if action == "resume":
                    self.state = self.STATE_PLAYING
                elif action == "menu":
                    self.state = self.STATE_MENU

            # ── Game over ─────────────────────────────────────
            elif self.state == self.STATE_GAMEOVER:
                action = self.gameover_screen.handle_event(event)
                if action == "restart":
                    self._setup_game()
                    self.state = self.STATE_PLAYING
                elif action == "menu":
                    self.state = self.STATE_MENU

    # ── Update ────────────────────────────────────────────────

    def _update(self, dt: int):
        self.bg.update()                       # always scroll bg

        if self.state != self.STATE_PLAYING:
            return

        now = pygame.time.get_ticks()

        # Player
        self.player.update(dt)

        # Difficulty scaling
        self.speed = min(OBS_SPEED_CAP,
                         OBS_BASE_SPEED + self.score // 8 * 0.4)
        self.spawn_interval = max(OBS_MIN_INTERVAL,
                                  OBS_BASE_INTERVAL - self.score // 8 * 50)

        # Spawn obstacles
        if now - self.last_obs_spawn > self.spawn_interval:
            self.obstacles.append(Obstacle(self.speed))
            self.last_obs_spawn = now

        # Spawn coins (every ~3 s)
        if now - self.last_coin_spawn > 3000:
            self.coins.append(Coin(self.speed))
            self.last_coin_spawn = now

        # Spawn power-ups (every ~12 s)
        if now - self.last_pup_spawn > 12000:
            self.powerups.append(PowerUp(self.speed))
            self.last_pup_spawn = now

        # Update obstacles
        passed = 0
        for obs in self.obstacles:
            obs.update()
            if obs.passed_player:
                passed += 1
        self.score    += passed
        self.obstacles = [o for o in self.obstacles if not o.off_screen and not o.passed_player]

        # Collision — obstacles
        for obs in self.obstacles:
            if self.player.rect.colliderect(obs.hitbox):
                survived = self.player.absorb_hit()
                if survived:
                    self.sounds.play("powerup")
                    self.obstacles.remove(obs)
                    break
                else:
                    self._trigger_gameover()
                    return

        # Update & collect coins
        for coin in self.coins[:]:
            coin.update()
            if coin.off_screen:
                self.coins.remove(coin)
                continue
            if self.player.rect.colliderect(coin.rect):
                self.score += COIN_VALUE
                self.sounds.play("coin")
                self.coins.remove(coin)

        # Update & collect power-ups
        for pup in self.powerups[:]:
            pup.update()
            if pup.off_screen:
                self.powerups.remove(pup)
                continue
            if self.player.rect.colliderect(pup.rect):
                if pup.kind == "shield":
                    self.player.activate_shield()
                elif pup.kind == "double_jump":
                    self.player.activate_double_jump()
                self.sounds.play("powerup")
                self.powerups.remove(pup)

        # Milestone sound
        milestone = self.score // MILESTONE_INTERVAL
        if milestone > self.last_milestone:
            self.sounds.play("milestone")
            self.last_milestone = milestone

    def _trigger_gameover(self):
        self.sounds.play("hit")
        if self.score > self.highscore:
            self.highscore  = self.score
            self.is_new_best = True
            write_highscore(self.highscore)
        self.state = self.STATE_GAMEOVER

    # ── Draw ──────────────────────────────────────────────────

    def _draw(self):
        # Background is always drawn
        self.bg.draw(self.screen)

        if self.state in (self.STATE_PLAYING,
                          self.STATE_PAUSED,
                          self.STATE_GAMEOVER):
            # Game objects
            for obs  in self.obstacles: obs.draw(self.screen)
            for coin in self.coins:     coin.draw(self.screen)
            for pup  in self.powerups:  pup.draw(self.screen)
            self.player.draw(self.screen)

            # HUD
            self.hud.draw(
                self.screen, self.score, self.highscore,
                self.speed,
                self.player.has_shield,
                self.player.has_double_jump,
            )

        # Overlay screens
        if self.state == self.STATE_MENU:
            self.menu_screen.draw(self.screen, self.highscore)
        elif self.state == self.STATE_PAUSED:
            self.pause_screen.draw(self.screen)
        elif self.state == self.STATE_GAMEOVER:
            self.gameover_screen.draw(self.screen, self.score,
                                      self.highscore, self.is_new_best)

        pygame.display.update()

    # ── Quit ──────────────────────────────────────────────────

    def _quit(self):
        write_highscore(self.highscore)
        pygame.quit()
        sys.exit()


# ══════════════════════════════════════════════════════════════
#  Entry point
# ══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    Game().run()