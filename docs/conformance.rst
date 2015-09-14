###########
Conformance
###########

Open Office XML is standardized by
`ECMA-376 <http://www.ecma-international.org/publications/standards/Ecma-376.htm>`_.

To the greatest degree possible,
PyDocX intends to conform with this
and subsequent standards.

17.9 Numbering
##############

======= ============================================= ===========
Section Description                                   Implemented
======= ============================================= ===========
17.9.1  abstractNum                                   true
17.9.2  abstractNumId                                 true
17.9.3  ilvl                                          true
17.9.4  isLgl                                         false
17.9.5  lvl (override)                                false
17.9.6  lvl                                           true
17.9.7  lvlJc                                         false
17.9.8  lvlOverride                                   false
17.9.9  lvlPictPulletId                               false
17.9.10 lvlRestart                                    false
17.9.11 lvlText                                       false
17.9.12 multiLevelType                                false
17.9.13 name                                          false
17.9.14 nsid                                          false
17.9.15 num                                           true
17.9.16 numbering                                     true
17.9.17 numFmt                                        true
17.9.18 numId                                         true
17.9.19 numIdMacAtCleanup                             false
17.9.20 numPicBullet                                  false
17.9.21 numStyleLink                                  false
17.9.22 pPr                                           false
17.9.23 pStyle                                        false
17.9.24 rPr                                           false
17.9.25 start                                         false
17.9.26 startOverride                                 false
17.9.27 styleLink                                     false
17.9.28 suff                                          false
17.9.29 tmpl                                          false
======= ============================================= ===========

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
