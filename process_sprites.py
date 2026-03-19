import pygame
import os

def process_single(in_path, out_path, size):
    try:
        img = pygame.image.load(in_path).convert_alpha()
    except Exception as e:
        print(f"Failed to load {in_path}: {e}")
        return
    w, h = img.get_size()
    
    # replace white with transparent
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.get_at((x, y))
            if r > 240 and g > 240 and b > 240:
                img.set_at((x, y), (255, 255, 255, 0))
    
    rect = img.get_bounding_rect()
    if rect.width > 0:
        cropped = img.subsurface(rect).copy()
        scaled = pygame.transform.smoothscale(cropped, size)
        pygame.image.save(scaled, out_path)
        print(f"Saved {out_path}")

def process_sheet(in_path, out_prefix, count, size):
    try:
        img = pygame.image.load(in_path).convert_alpha()
    except Exception as e:
        print(f"Failed to load {in_path}: {e}")
        return
    w, h = img.get_size()
    
    for x in range(w):
        for y in range(h):
            r, g, b, a = img.get_at((x, y))
            if r > 240 and g > 240 and b > 240:
                img.set_at((x, y), (255, 255, 255, 0))
    
    visited = set()
    blobs = []
    
    scale = 2 # skip pixels for speed
    for x in range(0, w, scale):
        for y in range(0, h, scale):
            if (x, y) not in visited:
                a = img.get_at((x,y))[3]
                if a > 0:
                    stack = [(x,y)]
                    blob = []
                    while stack:
                        cx, cy = stack.pop()
                        if (cx, cy) in visited: continue
                        visited.add((cx,cy))
                        
                        if cx < 0 or cy < 0 or cx >= w or cy >= h: continue
                        if img.get_at((cx,cy))[3] == 0: continue
                        
                        blob.append((cx, cy))
                        stack.extend([(cx+1, cy), (cx-1, cy), (cx, cy+1), (cx, cy-1)])
                    if len(blob) > 200:
                        blobs.append(blob)
                visited.add((x,y))
                
    blobs.sort(key=len, reverse=True)
    for i, blob in enumerate(blobs[:count]):
        xs = [p[0] for p in blob]
        ys = [p[1] for p in blob]
        x1, x2 = min(xs), max(xs)
        y1, y2 = min(ys), max(ys)
        rect = pygame.Rect(x1, y1, x2-x1+1, y2-y1+1)
        cropped = img.subsurface(rect).copy()
        scaled = pygame.transform.smoothscale(cropped, size)
        pygame.image.save(scaled, f"{out_prefix}_{i}.png")
        print(f"Saved {out_prefix}_{i}.png")

if __name__ == "__main__":
    pygame.display.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    if not os.path.exists("assets/images"):
        os.makedirs("assets/images")
    process_sheet('/home/samir/.gemini/antigravity/brain/2ff953e5-d799-44ae-8aab-9e9f14425448/player_run_1773935499437.png', 'assets/images/player_run', 4, (60, 80))
    process_single('/home/samir/.gemini/antigravity/brain/2ff953e5-d799-44ae-8aab-9e9f14425448/player_jump_1773936081232.png', 'assets/images/player_jump_0.png', (60, 80))
    process_single('/home/samir/.gemini/antigravity/brain/2ff953e5-d799-44ae-8aab-9e9f14425448/player_slide_1773936237947.png', 'assets/images/player_slide_0.png', (80, 40))
    process_single('/home/samir/.gemini/antigravity/brain/2ff953e5-d799-44ae-8aab-9e9f14425448/obs_fly_1773936281079.png', 'assets/images/obs_fly.png', (45, 40))
