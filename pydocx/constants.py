from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

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
# English Metric Units
EMUS_PER_PIXEL = 9525
USE_ALIGNMENTS = True

# https://en.wikipedia.org/wiki/Twip
TWIPS_PER_POINT = 20

# TODO These alignment values are for traditional conformance. Strict
# conformance uses different values
JUSTIFY_CENTER = 'center'
JUSTIFY_LEFT = 'left'
JUSTIFY_RIGHT = 'right'

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
    # List Style Types
    'list-style-type-cardinalText': {
        'list-style-type': 'decimal',
    },
    'list-style-type-decimal': {
        'list-style-type': 'decimal',
    },
    'list-style-type-decimalEnclosedCircle': {
        'list-style-type': 'decimal',
    },
    'list-style-type-decimalEnclosedFullstop': {
        'list-style-type': 'decimal',
    },
    'list-style-type-decimalEnclosedParen': {
        'list-style-type': 'decimal',
    },
    'list-style-type-decimalZero': {
        'list-style-type': 'decimal-leading-zero',
    },
    'list-style-type-lowerLetter': {
        'list-style-type': 'lower-alpha',
    },
    'list-style-type-lowerRoman': {
        'list-style-type': 'lower-roman',
    },
    'list-style-type-none': {
        'list-style-type': 'none',
    },
    'list-style-type-ordinalText': {
        'list-style-type': 'decimal',
    },
    'list-style-type-upperLetter': {
        'list-style-type': 'upper-alpha',
    },
    'list-style-type-upperRoman': {
        'list-style-type': 'upper-roman',
    },
}
