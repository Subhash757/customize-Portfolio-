"""
Spider-Man Cursor Trail Effect 🕷️
====================================
Red-to-blue shifting cursor with glowing trail.
Controls: Move your mouse. Press ESC to quit.
Requirements: pip install pygame pyautogui
"""

import pygame
import pyautogui
import sys
import math

# ── Config ────────────────────────────────────────────────────────────────────
FPS         = 60
TRAIL_LEN   = 25
MAIN_RADIUS = 20
BG_COLOR    = (0, 0, 0)

# Spider-Man palette
RED   = (204,  0,   0)    # #cc0000
BLUE  = (  0, 51, 153)    # #003399
WHITE = (255, 255, 255)

# ── Helpers ───────────────────────────────────────────────────────────────────
def lerp_color(c1, c2, t):
    """Linear interpolate between two RGB colors. t in [0, 1]."""
    return (
        int(c1[0] + (c2[0] - c1[0]) * t),
        int(c1[1] + (c2[1] - c1[1]) * t),
        int(c1[2] + (c2[2] - c1[2]) * t),
    )

def spiderman_color(phase):
    """
    phase: 0..1 cycling value
    0.0 → red, 0.5 → blue, 1.0 → red (smooth ping-pong)
    """
    # ping-pong: 0→1→0
    t = (math.sin(phase * math.pi * 2) + 1) / 2   # 0..1
    return lerp_color(RED, BLUE, t)

def draw_glow(surface, color, pos, radius, alpha=255):
    """
    Layered glow: 3 circles, progressively smaller and brighter.
    """
    x, y = int(pos[0]), int(pos[1])
    glow_layers = [
        (radius + 18, max(0, alpha // 8)),
        (radius + 10, max(0, alpha // 4)),
        (radius + 4,  max(0, alpha // 2)),
        (radius,      alpha),
    ]
    for r, a in glow_layers:
        if r <= 0:
            continue
        surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        pygame.draw.circle(surf, (*color, a), (r, r), r)
        surface.blit(surf, (x - r, y - r), special_flags=pygame.BLEND_RGBA_ADD)

def draw_spider_web_hint(surface, pos, radius, color, alpha):
    """Small decorative web lines radiating from cursor."""
    x, y = int(pos[0]), int(pos[1])
    for angle_deg in range(0, 360, 45):
        angle = math.radians(angle_deg)
        end_x = x + int(math.cos(angle) * (radius + 14))
        end_y = y + int(math.sin(angle) * (radius + 14))
        line_surf = pygame.Surface((abs(end_x - x) * 2 + 10, abs(end_y - y) * 2 + 10), pygame.SRCALPHA)
        # draw on main surface directly with alpha trick
        line_color = (*color, max(0, alpha // 3))
        pygame.draw.line(surface, (line_color[0], line_color[1], line_color[2]),
                         (x, y), (end_x, end_y), 1)

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    info = pygame.display.Info()
    W, H = info.current_w, info.current_h

    # Borderless window covering full screen
    screen = pygame.display.set_mode((W, H), pygame.NOFRAME)
    pygame.display.set_caption("🕷️ Spider-Man Cursor Trail")
    clock = pygame.time.Clock()

    pyautogui.FAILSAFE = False

    trail  = []    # list of (x, y) screen positions
    phase  = 0.0   # hue phase [0..∞]

    font_big  = pygame.font.SysFont("consolas", 15, bold=True)
    font_sm   = pygame.font.SysFont("consolas", 12)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0

        # ── Events ─────────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

        # ── Real mouse position ─────────────────────────────────────────
        mx, my = pyautogui.position()

        trail.append((mx, my))
        if len(trail) > TRAIL_LEN:
            trail.pop(0)

        # Advance phase (full red→blue→red cycle in ~2 seconds)
        phase = (phase + 0.008) % 1.0

        # ── Draw ───────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # Trail dots (oldest first, smallest + most transparent)
        for i, (tx, ty) in enumerate(trail):
            t = i / max(len(trail) - 1, 1)           # 0=oldest, 1=newest
            # Color: oldest dots are blue-tinted, newest match cursor
            trail_phase = (phase - (1 - t) * 0.35) % 1.0
            color = spiderman_color(trail_phase)

            # Size: shrink from MAIN_RADIUS → 2 for oldest
            radius = max(2, int(2 + t * (MAIN_RADIUS - 2)))
            # Alpha: fade from 0 → 230
            alpha  = int(t * 230)

            if radius > 0 and alpha > 0:
                dot_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(dot_surf, (*color, alpha), (radius, radius), radius)
                screen.blit(dot_surf, (tx - radius, ty - radius))

        # Main cursor: glowing layered circles
        main_color = spiderman_color(phase)
        draw_glow(screen, main_color, (mx, my), MAIN_RADIUS)

        # Spider-web accent lines
        web_color = lerp_color(main_color, WHITE, 0.3)
        for angle_deg in range(0, 360, 45):
            angle = math.radians(angle_deg)
            ex = mx + int(math.cos(angle) * (MAIN_RADIUS + 16))
            ey = my + int(math.sin(angle) * (MAIN_RADIUS + 16))
            pygame.draw.line(screen, web_color, (mx, my), (ex, ey), 1)

        # ── HUD ─────────────────────────────────────────────────────────
        r, g, b = main_color
        hud1 = font_big.render("🕷️  SPIDER-MAN TRAIL", True, (r, g, b))
        hud2 = font_sm.render(f"Mouse: ({mx}, {my})   |   Press ESC to quit", True, (80, 80, 80))
        screen.blit(hud1, (12, 12))
        screen.blit(hud2, (12, 34))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
