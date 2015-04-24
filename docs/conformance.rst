###########
Conformance
###########

Open Office XML is standardized by
`ECMA-376 <http://www.ecma-international.org/publications/standards/Ecma-376.htm>`_.

To the greatest degree possible,
PyDocX intends to conform with this
and subsequent standards.

Deviations
##########

In some cases,
it was necessary to deviate
from the specification.
Such deviations
should be only done
with justification,
and minimally.
All intended deviations
shall be documented here.
Any undocumented deviations
are bugs.

Missing val attribute in underline tag
======================================

* In the event that the
  ``val`` attribute
  is missing
  from a ``u`` (``ST_Underline`` type),
  we treat the underline as off,
  or none.
  See also
  http://msdn.microsoft.com/en-us/library/ff532016%28v=office.12%29.aspx

   If the val attribute is not specified,
   Word defaults to the value defined
   in the style hierarchy
   and then to no underline.
