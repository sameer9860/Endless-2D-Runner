import os

with open('main.py', 'r') as f:
    content = f.read()

part1_old = '''                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.player.jump()
                    elif event.key == pygame.K_ESCAPE:'''

part1_new = '''                    if event.key in (pygame.K_SPACE, pygame.K_UP):
                        self.player.jump()
                    elif event.key == pygame.K_DOWN:
                        self.player.slide()
                    elif event.key == pygame.K_ESCAPE:'''

content = content.replace(part1_old, part1_new)

part2_old = '''            ("SPACE / ↑  — Jump (hold for higher)", self.fonts["sm"], C_TEXT, 210),
            ("Double-jump with 2↑ power-up",        self.fonts["sm"], C_TEXT, 245),
            ("Collect  coins  for bonus points",     self.fonts["sm"], C_TEXT, 280),
            ("SHD  shield survives one hit",         self.fonts["sm"], C_TEXT, 315),
            ("Speed increases as your score climbs", self.fonts["sm"], C_TEXT_DIM, 365),'''

part2_new = '''            ("SPACE / ↑  — Jump (hold for higher)", self.fonts["sm"], C_TEXT, 210),
            ("↓          — Slide / Duck",             self.fonts["sm"], C_TEXT, 240),
            ("Double-jump with 2↑ power-up",        self.fonts["sm"], C_TEXT, 270),
            ("Collect  coins  for bonus points",     self.fonts["sm"], C_TEXT, 300),
            ("SHD  shield survives one hit",         self.fonts["sm"], C_TEXT, 330),
            ("Speed increases as your score climbs", self.fonts["sm"], C_TEXT_DIM, 370),'''

content = content.replace(part2_old, part2_new)

with open('main.py', 'w') as f:
    f.write(content)

print("Patch applied to main.py successfully!")
