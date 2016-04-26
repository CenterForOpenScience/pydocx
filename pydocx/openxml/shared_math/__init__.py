from pydocx.openxml.shared_math.accent import Accent
from pydocx.openxml.shared_math.accent_properties import AccentProperties
from pydocx.openxml.shared_math.align import Align
from pydocx.openxml.shared_math.align_scripts import AlignScripts
from pydocx.openxml.shared_math.argument_properties import ArgumentProperties
from pydocx.openxml.shared_math.argument_size import ArgumentSize
from pydocx.openxml.shared_math.bar import Bar
from pydocx.openxml.shared_math.bar_properties import BarProperties
from pydocx.openxml.shared_math.element import Element
from pydocx.openxml.shared_math.base_justification import BaseJustification
from pydocx.openxml.shared_math.border_box import BorderBox
from pydocx.openxml.shared_math.border_box_properties import BorderBoxProperties
from pydocx.openxml.shared_math.box import Box
from pydocx.openxml.shared_math.box_properties import BoxProperties
from pydocx.openxml.shared_math.control_properties import ControlProperties
from pydocx.openxml.shared_math.degree import Degree
from pydocx.openxml.shared_math.delimiter_function import DelimiterFunction
from pydocx.openxml.shared_math.delimiter_properties import DelimiterProperties
from pydocx.openxml.shared_math.denominator import Denominator
from pydocx.openxml.shared_math.equation_array_function import EquationArrayFunction
from pydocx.openxml.shared_math.equation_array_properties import EquationArrayProperties
from pydocx.openxml.shared_math.fraction_function import FractionFunction
from pydocx.openxml.shared_math.nary_operator_function import NaryOperatorFunction  # noqa
from pydocx.openxml.shared_math.nary_properties import NaryProperties
from pydocx.openxml.shared_math.numerator import Numerator
from pydocx.openxml.shared_math.matrix_function import MatrixFunction
from pydocx.openxml.shared_math.maximum_distribution import MaximumDistribution
from pydocx.openxml.shared_math.object_distribution import ObjectDistribution
from pydocx.openxml.shared_math.omath import OMath
from pydocx.openxml.shared_math.phantom_function import PhantomFunction
from pydocx.openxml.shared_math.row_spacing import RowSpacing
from pydocx.openxml.shared_math.row_spacing_rule import RowSpacingRule
from pydocx.openxml.shared_math.subscript import Subscript
from pydocx.openxml.shared_math.superscript import Superscript
from pydocx.openxml.shared_math.superscript_function import SuperscriptFunction

Element.children.types.add(FractionFunction)


__all__ = [
    'Accent',
    'AccentProperties',
    'Align',
    'AlignScripts',
    'ArgumentProperties',
    'ArgumentSize',
    'Bar',
    'BarProperties',
    'Element',
    'BaseJustification',
    'BorderBox',
    'BorderBoxProperties',
    'Box',
    'BoxProperties',
    'ControlProperties',
    'Degree',
    'DelimiterFunction',
    'DelimiterProperties',
    'Denominator',
    'EquationArrayFunction',
    'EquationArrayProperties',
    'FractionFunction'
    'NaryOperatorFunction',
    'NaryProperties',
    'Numerator',
    'MatrixFunction',
    'MaximumDistribution',
    'ObjectDistribution',
    'OMath',
    'PhantomFunction',
    'RowSpacing',
    'RowSpacingRule',
    'Subscript',
    'Superscript',
    'SuperscriptFunction'
]
