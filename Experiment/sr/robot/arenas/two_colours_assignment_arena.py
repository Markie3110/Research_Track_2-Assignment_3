from __future__ import division

from math import cos, pi, sin

import pygame
import random
from pygame.rect import Rect

from arena import ARENA_MARKINGS_COLOR, ARENA_MARKINGS_WIDTH, Arena
from ..markers import Token
from ..vision import MARKER_TOKEN_GOLD, MARKER_TOKEN_SILVER

HOME_ZONE_SIZE = 2.5

INNER_CIRCLE_RADIUS = 0.9
OUTER_CIRCLE_RADIUS = 2.4  # Some tokens are at 1200ish, others at 1270ish
TOKENS_PER_CIRCLE = 6
PEDESTAL_COLOR = (0x80, 0x80, 0x80)


class GoldToken(Token):
    def __init__(self, arena, marker_number):
        super(GoldToken, self).__init__(arena, marker_number,
                                        marker_type=MARKER_TOKEN_GOLD, damping=10)

    @property
    def surface_name(self):
        return 'sr/token_gold_grabbed.png' if self.grabbed else 'sr/token.png'


class SilverToken(Token):
    def __init__(self, arena, marker_number):
        super(SilverToken, self).__init__(arena, marker_number,
                                          marker_type=MARKER_TOKEN_SILVER, damping=10)

    @property
    def surface_name(self):
        return 'sr/token_silver_grabbed.png' if self.grabbed else 'sr/token_silver.png'


class TwoColoursAssignmentArena(Arena):
    size = (5.75, 5.75)

    start_locations = [(-2.6, -2.6),
                       (2.6, -2.6),
                       (2.6, 2.6),
                       (-2.6, 2.6)]

    start_headings = [0.25 * pi,
                      0.75 * pi,
                      -0.75 * pi,
                      -0.25 * pi]

    def __init__(self, objects=None, wall_markers=False):
        super(TwoColoursAssignmentArena, self).__init__(objects, wall_markers)

        def place_token_circle(radius, number_offset=0, angle_offset=0.25 * pi,
                               rotate_silvers=0.0):
            for i in range(TOKENS_PER_CIRCLE):
                token_type = GoldToken
                rotation_amount = 0
                token = token_type(self, number_offset + i)
                #angle = angle_offset + (2 * pi / TOKENS_PER_CIRCLE) * i
                angle = random.uniform(0, 2 * pi)
                #radius_random = random.uniform(0.9, 2.4)
                token.location = (cos(angle) * radius, sin(angle) * radius)
                token.heading = rotation_amount
                self.objects.append(token)

        place_token_circle(OUTER_CIRCLE_RADIUS, number_offset=TOKENS_PER_CIRCLE,
                           angle_offset=1.5 * pi, rotate_silvers=pi / 4)

    def draw_background(self, surface, display):

        def draw_pedestal():
            pygame.draw.rect(surface, PEDESTAL_COLOR,
                             # Pedestal is 4ft wide.
                             Rect(display.to_pixel_coord((-0.6096, -0.6096)),
                                  display.to_pixel_dimension((1.2192, 1.2192))))

        def line(start, end):
            pygame.draw.line(surface, ARENA_MARKINGS_COLOR,
                             start, end, ARENA_MARKINGS_WIDTH)

        # Home zones
        def draw_corner_triangle(corner, width, depth):
            x, y = corner
            wall_corner_1 = display.to_pixel_coord((x + width, y))
            wall_corner_2 = display.to_pixel_coord((x, y + depth))
            line(wall_corner_1, wall_corner_2)

        super(TwoColoursAssignmentArena, self).draw_background(surface, display)
        draw_pedestal()

        draw_corner_triangle((self.left, self.top), HOME_ZONE_SIZE, HOME_ZONE_SIZE)
        draw_corner_triangle((self.right, self.top), -HOME_ZONE_SIZE, HOME_ZONE_SIZE)
        draw_corner_triangle((self.right, self.bottom), -HOME_ZONE_SIZE, -HOME_ZONE_SIZE)
        draw_corner_triangle((self.left, self.bottom), HOME_ZONE_SIZE, -HOME_ZONE_SIZE)
