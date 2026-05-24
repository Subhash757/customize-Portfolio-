"""
Rainbow Cursor Trail Effect
============================
Controls: Move your mouse to draw rainbow trails. Press ESC to quit.
Requirements: pip install pygame pyautogui
"""

import pygame
import pyautogui
import colorsys
import sys
import math

# ── Config ────────────────────────────────────────────────────────────────────
FPS          = 60
TRAIL_LEN    = 20       # number of trail dots
MAIN_RADIUS  = 20       # main circle radius (px)
WINDOW_W     = 800
WINDOW_H     = 600
BG_COLOR     = (0, 0, 0)

# ── Helpers ───────────────────────────────────────────────────────────────────
def hsl_to_rgb(h, s, l):
    """Convert HSL (0-1 range) to RGB (0-255)."""
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r * 255), int(g * 255), int(b * 255))

def draw_glow_circle(surface, color, pos, radius, alpha=255):
    """Draw a glowing circle using layered semi-transparent surfaces."""
    x, y = int(pos[0]), int(pos[1])
    for layer in range(3, 0, -1):
        r = radius + layer * 6
        a = max(0, alpha // (layer * 2 + 1))
        glow_surf = pygame.Surface((r * 2, r * 2), pygame.SRCALPHA)
        glow_color = (*color, a)
        pygame.draw.circle(glow_surf, glow_color, (r, r), r)
        surface.blit(glow_surf, (x - r, y - r), special_flags=pygame.BLEND_RGBA_ADD)
    # Solid core
    core_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
    pygame.draw.circle(core_surf, (*color, alpha), (radius, radius), radius)
    surface.blit(core_surf, (x - radius, y - radius))

# ── Main ──────────────────────────────────────────────────────────────────────
def main():
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H), pygame.NOFRAME | pygame.RESIZABLE)
    pygame.display.set_caption("🌈 Rainbow Cursor Trail — ESC to quit")
    clock = pygame.time.Clock()

    # Disable pyautogui failsafe briefly
    pyautogui.FAILSAFE = False

    trail = []       # list of (x, y) positions
    hue   = 0.0      # current hue [0..1]

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

        # ── Get real mouse position (window coords) ─────────────────────
        rx, ry = pygame.mouse.get_pos()

        # Record trail position
        trail.append((rx, ry))
        if len(trail) > TRAIL_LEN:
            trail.pop(0)

        # Advance hue (full rainbow cycle in ~3 seconds)
        hue = (hue + 0.005) % 1.0

        # ── Draw ───────────────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # Draw trail (oldest → newest)
        for i, (tx, ty) in enumerate(trail):
            t = i / max(len(trail) - 1, 1)          # 0 (oldest) → 1 (newest)
            trail_hue = (hue - (1 - t) * 0.25) % 1.0
            color = hsl_to_rgb(trail_hue, 1.0, 0.55)
            radius = max(2, int(2 + t * (MAIN_RADIUS - 2)))  # 2 → MAIN_RADIUS
            alpha  = int(30 + t * 225)                        # fade in

            dot_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(dot_surf, (*color, alpha), (radius, radius), radius)
            screen.blit(dot_surf, (int(tx) - radius, int(ty) - radius))

        # Draw main glowing cursor circle
        main_color = hsl_to_rgb(hue, 1.0, 0.6)
        draw_glow_circle(screen, main_color, (rx, ry), MAIN_RADIUS)

        # HUD
        font = pygame.font.SysFont("consolas", 14)
        hud = font.render(f"🌈 Rainbow Trail  |  {FPS} FPS  |  Press ESC to quit", True, (100, 100, 100))
        screen.blit(hud, (10, 10))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
