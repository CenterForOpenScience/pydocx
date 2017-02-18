from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.break_on_binary_operators import BreakOnBinaryOperators
from pydocx.openxml.shared_math.break_on_binary_subtraction import BreakOnBinarySubtraction
from pydocx.openxml.shared_math.default_justification import DefaultJustification
from pydocx.openxml.shared_math.inter_equation_spacing import InterEquationSpacing
from pydocx.openxml.shared_math.intra_equation_spacing import IntraEquationSpacing
from pydocx.openxml.shared_math.integral_limit_locations import IntegralLimitLocations
from pydocx.openxml.shared_math.small_fraction import SmallFraction
from pydocx.openxml.shared_math.left_margin import LeftMargin
from pydocx.openxml.shared_math.math_font import MathFont
from pydocx.openxml.shared_math.nary_limit_location import NaryLimitLocation
from pydocx.openxml.shared_math.pre_equation_spacing import PreEquationSpacing
from pydocx.openxml.shared_math.post_equation_spacing import PostEquationSpacing
from pydocx.openxml.shared_math.right_margin import RightMargin
from pydocx.openxml.shared_math.use_display_math_defaults import UseDisplayMathDefaults
from pydocx.openxml.shared_math.wrap_indent import WrapIndent
from pydocx.openxml.shared_math.wrap_right import WrapRight


class MathProperties(XmlModel):

    XML_TAG = 'mathPr'

    children = XmlCollection(
        BreakOnBinaryOperators,
        BreakOnBinarySubtraction,
        DefaultJustification,
        InterEquationSpacing,
        IntraEquationSpacing,
        IntegralLimitLocations,
        SmallFraction,
        LeftMargin,
        MathFont,
        NaryLimitLocation,
        PreEquationSpacing,
        PostEquationSpacing,
        RightMargin,
        UseDisplayMathDefaults,
        WrapIndent,
        WrapRight,
    )
