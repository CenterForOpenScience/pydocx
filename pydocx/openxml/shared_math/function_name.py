from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

from pydocx.models import XmlModel, XmlCollection
from pydocx.openxml.shared_math.accent import Accent
from pydocx.openxml.shared_math.bar import Bar
from pydocx.openxml.shared_math.box import Box
from pydocx.openxml.shared_math.border_box import BorderBox
from pydocx.openxml.shared_math.delimiter_function import DelimiterFunction
from pydocx.openxml.shared_math.equation_array_function import EquationArrayFunction
from pydocx.openxml.shared_math.fraction_function import FractionFunction
from pydocx.openxml.shared_math.function_apply_function import FunctionApplyFunction
from pydocx.openxml.shared_math.group_character_function import GroupCharacterFunction
from pydocx.openxml.shared_math.lower_limit_function import LowerLimitFunction
from pydocx.openxml.shared_math.upper_limit_function import UpperLimitFunction
from pydocx.openxml.shared_math.matrix_function import MatrixFunction
from pydocx.openxml.shared_math.nary_operator_function import NaryOperatorFunction
from pydocx.openxml.shared_math.phantom_function import PhantomFunction
# from pydocx.openxml.shared_math.radical_function import RadicalFunction
# from pydocx.openxml.shared_math.pre_sub_superscript_function import PreSubSuperscriptFunction
# from pydocx.openxml.shared_math.subscript_function import SubscriptFunction
# from pydocx.openxml.shared_math.sub_superscript_function import SubSuperscriptFunction
# from pydocx.openxml.shared_math.superscript_function import SuperscriptFunction
from pydocx.openxml.wordprocessing.run import Run


class FunctionName(XmlModel):
    XML_TAG = 'fName'
    children = XmlCollection(
        Accent,
        Bar,
        Box,
        BorderBox,
        DelimiterFunction,
        EquationArrayFunction,
        FractionFunction,
        FunctionApplyFunction,
        GroupCharacterFunction,
        LowerLimitFunction,
        UpperLimitFunction,
        MatrixFunction,
        NaryOperatorFunction,
        PhantomFunction,
        # RadicalFunction,
        # PreSubSuperscriptFunction,
        # SubscriptFunction,
        # SubSuperscriptFunction,
        # SuperscriptFunction,
        Run
    )
