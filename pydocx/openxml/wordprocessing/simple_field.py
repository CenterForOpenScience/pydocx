# coding: utf-8
from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)

import re

from pydocx.models import XmlModel, XmlCollection, XmlAttribute

from pydocx.openxml.wordprocessing.hyperlink import Hyperlink
from pydocx.openxml.wordprocessing.run import Run
from pydocx.openxml.wordprocessing.smart_tag_run import SmartTagRun
from pydocx.openxml.wordprocessing.inserted_run import InsertedRun
from pydocx.openxml.wordprocessing.deleted_run import DeletedRun
from pydocx.openxml.wordprocessing.sdt_run import SdtRun


class SimpleField(XmlModel):
    XML_TAG = 'fldSimple'

    instr = XmlAttribute()

    children = XmlCollection(
        Run,
        Hyperlink,
        SmartTagRun,
        InsertedRun,
        DeletedRun,
        SdtRun,
    )

    def _parse_instr_into_field_type_and_arg_string(self):
        return re.match('^\s*([^\s]+)\s*(.*)$', self.instr)

    def _parse_instr_arg_string_to_args(self, arg_string):
        return re.findall(r'\s*(?:"([^"]+)"|([^\s]+))+', arg_string)

    def parse_instr(self):
        m = self._parse_instr_into_field_type_and_arg_string()
        if not m:
            return
        field_type = m.group(1)
        raw_field_args = m.group(2)
        if not raw_field_args:
            return field_type, None
        m = self._parse_instr_arg_string_to_args(raw_field_args)
        if not m:
            return field_type, None
        field_args = [
            args[0] if args[0] else args[1]
            for args in m
        ]
        return field_type, field_args
