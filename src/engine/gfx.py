from contextlib import contextmanager

import pygame
import pygame.gfxdraw

__all__ = ["GFX"]


class GFX:
    def __init__(self, surf: pygame.Surface):
        self.surf = surf
        self.world_center = pygame.Vector2(0, 0)
        self.world_scale = 1
        self.ui_scale = 1

        self.translation = pygame.Vector2()

    def blit(self, surf, **anchor):

        r = surf.get_rect(**anchor)
        r.topleft += self.translation
        self.surf.blit(surf, r)

        return r

    # Draw functions

    def rect(self, x, y, w, h, color, width=0, anchor: str = None):

        r = pygame.Rect(x, y, w * self.world_scale, h * self.world_scale)

        if anchor:
            setattr(r, anchor, (x, y))

        r.topleft += self.translation

        pygame.draw.rect(self.surf, color, r, width)

    def box(self, rect, color):
        rect = pygame.Rect(rect)
        rect.topleft += self.translation
        pygame.gfxdraw.box(self.surf, rect, color)

    def grid(self, surf, pos, blocks, steps, color=(255, 255, 255, 100)):

        top, left = self.scale_world_pos(*pos)
        bottom = top + steps * self.world_scale
        right = left + steps * self.world_scale
        for x in range(blocks[0] + 1):
            pygame.gfxdraw.line(surf, x, top, x, bottom, color)
        for y in range(blocks[0] + 1):
            pygame.gfxdraw.line(surf, left, y, right, y, color)

    def fill(self, color):
        self.surf.fill(color)

    def scroll(self, dx, dy):
        self.surf.scroll(dx, dy)

    @contextmanager
    def focus(self, rect):

        rect = pygame.Rect(rect)

        previous_clip = self.surf.get_clip()
        self.surf.set_clip(rect)
        self.translation = pygame.Vector2(rect.topleft)
        yield
        self.surf.set_clip(previous_clip)
        if previous_clip:
            self.translation = pygame.Vector2(previous_clip.topleft)