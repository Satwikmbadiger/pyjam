from contextlib import contextmanager
from functools import lru_cache
from math import exp
from random import randrange, uniform
from typing import Tuple

import pygame


def vec2int(vec):
    return int(vec[0]), int(vec[1])


@lru_cache()
def load_img(path, alpha=False):
    if alpha:
        return pygame.image.load(path).convert_alpha()
    return pygame.image.load(path).convert()


@lru_cache()
def get_tile(tilesheet: pygame.Surface, size, x, y, w=1, h=1):
    return tilesheet.subsurface(x * size, y * size, w * size, h * size)


def mix(color1, color2, t):
    return (
        round((1 - t) * color1[0] + t * color2[0]),
        round((1 - t) * color1[1] + t * color2[1]),
        round((1 - t) * color1[2] + t * color2[2]),
    )


def chrange(
    x: float,
    initial_range: Tuple[float, float],
    target_range: Tuple[float, float],
    power=1,
    flipped=False,
):
    normalised = (x - initial_range[0]) / (initial_range[1] - initial_range[0])
    normalised **= power
    if flipped:
        normalised = 1 - normalised
    return normalised * (target_range[1] - target_range[0]) + target_range[0]


def from_polar(r: float, angle: float):
    vec = pygame.Vector2()
    vec.from_polar((r, angle))
    return vec


def clamp(x, mini, maxi):
    if x < mini:
        return mini
    if x > maxi:
        return maxi
    return x


def angle_towards(start, goal, max_movement):
    start %= 360
    goal %= 360

    if abs(start - goal) > 180:
        return start + clamp(start - goal, -max_movement, max_movement)
    else:
        return start + clamp(goal - start, -max_movement, max_movement)


def random_in_rect(rect: pygame.Rect, x_range=(0.0, 1.0), y_range=(0.0, 1.0)):
    w, h = rect.size

    return (
        uniform(rect.x + w * x_range[0], rect.x + w * x_range[1]),
        uniform(rect.y + h * y_range[0], rect.y + h * y_range[1]),
    )


def random_in_surface(surf: pygame.Surface, max_retries=100):
    w, h = surf.get_size()
    color_key = surf.get_colorkey()
    with lock(surf):
        for _ in range(max_retries):
            pos = randrange(w), randrange(h)
            color = surf.get_at(pos)
            if not (color == color_key or color[3] == 0):
                # Pixel is not transparent.
                return pos
        return (w // 2, h // 2)


@contextmanager
def lock(surf):
    surf.lock()
    try:
        yield
    finally:
        surf.unlock()


def clamp_length(vec, maxi):

    if vec.length() > maxi:
        vec.scale_to_length(maxi)

    return vec


def part_perp_to(u, v):
    if v.length_squared() == 0:
        return u

    v = v.normalize()
    return u - v * v.dot(u)


def prop_in_rect(rect: pygame.Rect, prop_x: float, prop_y: float):
    pass


def bounce(x, f=0.2, k=60):

    s = max(x - f, 0.0)
    return min(x * x / (f * f), 1 + (2.0 / f) * s * exp(-k * s))


def exp_impulse(x, k):

    h = k * x
    return h * exp(1.0 - h)


def auto_crop(surf: pygame.Surface):

    rect = surf.get_bounding_rect()
    return surf.subsurface(rect)


def outline(surf: pygame.Surface, color=(255, 255, 255)):

    mask = pygame.mask.from_surface(surf)
    outline = mask.outline()
    output = pygame.Surface((surf.get_width() + 2, surf.get_height() + 2))

    with lock(output):
        for x, y in outline:
            for dx, dy in ((0, 1), (1, 0), (-1, 0), (0, -1)):
                output.set_at((x + dx + 1, y + dy + 1), color)

    output.blit(surf, (1, 1))

    output.set_colorkey(surf.get_colorkey())

    return output


@lru_cache(1000)
def overlay(image: pygame.Surface, color, alpha=255):
    img = pygame.Surface(image.get_size())
    img.set_colorkey((0, 0, 0))
    img.blit(image, (0, 0))

    mask = pygame.mask.from_surface(image)
    overlay = mask.to_surface(setcolor=color, unsetcolor=(255, 255, 0, 0))
    overlay.set_alpha(alpha)
    img.blit(overlay, (0, 0))

    return img


def random_in_rect_and_avoid(
    rect: pygame.Rect,
    avoid_positions,
    avoid_radius,
    max_trials=1000,
    force_y=None,
    default=None,
):
    for trial in range(max_trials):
        if force_y is not None:
            pos = uniform(rect.left, rect.right), force_y
        else:
            pos = random_in_rect(rect)

        # Any position is too close
        for p in avoid_positions:
            if p.distance_to(pos) < avoid_radius:
                break
        else:
            return pos

    return default


def random_rainbow_color(saturation=100, value=100):
    hue = randrange(0, 360)
    color = pygame.Color(0)
    color.hsva = hue, saturation, value, 100
    return color