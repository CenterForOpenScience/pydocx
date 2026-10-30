# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import math


def hex_to_rgb(value):
    """Return (red, green, blue) for the color given as #rrggbb."""

    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))


def brightness(hex_color):
    """A trick to determine the brightness of the color.
    More info about this here: http://alienryderflex.com/hsp.html
    """

    r, g, b = hex_to_rgb(hex_color)

    return math.sqrt(math.pow(r, 2) * .241 + math.pow(g, 2) * .691 + math.pow(b, 2) * .068)
