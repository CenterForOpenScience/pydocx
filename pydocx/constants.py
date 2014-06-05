from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

UPPER_ROMAN_TO_HEADING_VALUE = 'h2'
TAGS_CONTAINING_CONTENT = (
    't',
    'pict',
    'drawing',
    'delText',
    'ins',
)
TAGS_HOLDING_CONTENT_TAGS = (
    'p',
    'tbl',
    'sdt',
)

# http://openxmldeveloper.org/discussions/formats/f/15/p/396/933.aspx
EMUS_PER_PIXEL = 9525
USE_ALIGNMENTS = True

# https://en.wikipedia.org/wiki/Twip
TWIPS_PER_POINT = 20

JUSTIFY_CENTER = 'center'
JUSTIFY_LEFT = 'left'
JUSTIFY_RIGHT = 'right'

INDENTATION_RIGHT = 'right'
INDENTATION_LEFT = 'left'
INDENTATION_FIRST_LINE = 'firstLine'

POINTS_PER_EM = 12

PYDOCX_STYLES = {
    'insert': {
        'color': 'green',
    },
    'delete': {
        'color': 'red',
        'text-decoration': 'line-through',
    },
    'center': {
        'text-align': 'center',
    },
    'right': {
        'text-align': 'right',
    },
    'left': {
        'text-align': 'left',
    },
    'comment': {
        'color': 'blue',
    },
    'underline': {
        'text-decoration': 'underline',
    },
    'caps': {
        'text-transform': 'uppercase',
    },
    'small-caps': {
        'font-variant': 'small-caps',
    },
    'strike': {
        'text-decoration': 'line-through',
    },
    'hidden': {
        'visibility': 'hidden',
    },
    'tab': {
        'display': 'inline-block',
        'width': '4em',
    },
}
