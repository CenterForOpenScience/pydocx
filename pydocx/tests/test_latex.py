from itertools import chain

from pydocx.tests.document_builder import DocxBuilder as DXB
from pydocx.tests import (
    _LatexTranslationTestCase,
)


class ParagraphTestCase(_LatexTranslationTestCase):
    expected_output = '''
    AAA \n\n
    BBB \n\n
'''

    def get_xml(self):
        tags = [
            DXB.p_tag(text='AAA', bold=False),
            DXB.p_tag(text='BBB', bold=False),
        ]

        body = ''
        for tag in tags:
            body += tag
        xml = DXB.xml(body)
        return xml


class BoldTestCase(_LatexTranslationTestCase):
    expected_output = r'''
    \textbf{AAA}''' \
    + "\n" + '''BBB''' + "\n"

    def get_xml(self):
        tags = [
            DXB.p_tag(text='AAA', bold=True),
            DXB.p_tag(text='BBB', bold=True, val='false'),
        ]

        body = ''
        for tag in tags:
            body += tag
        xml = DXB.xml(body)
        return xml


class HyperlinkVanillaTestCase(_LatexTranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = r'''
        \href{www.google.com}{link}.
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link', is_bold=False))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkWithMultipleRunsTestCase(_LatexTranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = r'''
        \href{www.google.com}{link}.
    '''

    def get_xml(self):
        run_tags = [DXB.r_tag(i) for i in 'link']
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkNoTextTestCase(_LatexTranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = ''

    def get_xml(self):
        run_tags = []
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkNotInRelsDictTestCase(_LatexTranslationTestCase):
    relationship_dict = {
        # 'rId0': 'www.google.com', missing
    }

    expected_output = r'''
        link.
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link', is_bold=False))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        run_tags.append(DXB.r_tag('.', is_bold=False))
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class HyperlinkWithBreakTestCase(_LatexTranslationTestCase):
    relationship_dict = {
        'rId0': 'www.google.com',
    }

    expected_output = r'''
        \href{www.google.com}{link\\}
    '''

    def get_xml(self):
        run_tags = []
        run_tags.append(DXB.r_tag('link'))
        run_tags.append(DXB.r_tag(None, include_linebreak=True))
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class ImageNotInRelsDictTestCase(_LatexTranslationTestCase):
    relationship_dict = {
        # 'rId0': 'media/image1.jpeg',
    }
    expected_output = ''

    def get_xml(self):
        drawing = DXB.drawing(height=20, width=40, r_id='rId0')
        body = drawing

        xml = DXB.xml(body)
        return xml


class TableTag(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{tabular}{ l l }
          AAA & BBB \\
          CCC & DDD \\
        \end{tabular}
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('AAA')],
            [DXB.p_tag('BBB')],
            [DXB.p_tag('CCC')],
            [DXB.p_tag('DDD')],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class TableWithInvalidTag(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{tabular}{ l l }
          AAA & BBB \\
          & DDD \\
        \end{tabular}
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('AAA')],
            [DXB.p_tag('BBB')],
            # This tag may have CCC in it, however this tag has no meaning
            # pertaining to content.
            ['<w:invalidTag>CCC</w:invalidTag>'],
            [DXB.p_tag('DDD')],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class TableWithListAndParagraph(_LatexTranslationTestCase):
    expected_output = r'''
                \begin{tabular}{ l }
                \pbox{20cm}
                     {CCC \\ DDD} \\
                \end{tabular}
                '''

    def get_xml(self):
        els = [
            DXB.p_tag('CCC'),
            DXB.p_tag('DDD'),
        ]
        td = ''
        for el in els:
            td += el
        table = DXB.table(num_rows=1, num_columns=1, text=chain(
            [td],
        ))
        body = table
        xml = DXB.xml(body)
        return xml


class SimpleListTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA
            \item BBB
            \item CCC
        \end {enumerate}
    '''

    # Ensure its not failing somewhere and falling back to decimal
    numbering_dict = {
        '1': {
            '0': 'lowerLetter',
        }
    }

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', 0, 1),
            ('CCC', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class SingleListItemTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA
        \end {enumerate}
    '''

    # Ensure its not failing somewhere and falling back to decimal
    numbering_dict = {
        '1': {
            '0': 'lowerLetter',
        }
    }

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class ListWithContinuationTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA \\ BBB
            \item CCC
                \begin{tabular} {ll}
                        DDD & EEE \\
                        FFF & GGG \\
                \end{tabular}
            \item HHH
        \end{enumerate}
    '''

    def get_xml(self):
        table = DXB.table(num_rows=2, num_columns=2, text=chain(
            [DXB.p_tag('DDD')],
            [DXB.p_tag('EEE')],
            [DXB.p_tag('FFF')],
            [DXB.p_tag('GGG')],
        ))
        tags = [
            DXB.li(text='AAA', ilvl=0, numId=1),
            DXB.p_tag('BBB'),
            DXB.li(text='CCC', ilvl=0, numId=1),
            table,
            DXB.li(text='HHH', ilvl=0, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml


class ListWithMultipleContinuationTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA
                \begin{tabular} {l}
                        BBB\\
                \end{tabular}
                \begin{tabular} {l}
                        CCC\\
                \end{tabular}
            \item DDD
        \end{enumerate}
    '''

    def get_xml(self):
        table1 = DXB.table(num_rows=1, num_columns=1, text=chain(
            [DXB.p_tag('BBB')],
        ))
        table2 = DXB.table(num_rows=1, num_columns=1, text=chain(
            [DXB.p_tag('CCC')],
        ))
        tags = [
            DXB.li(text='AAA', ilvl=0, numId=1),
            table1,
            table2,
            DXB.li(text='DDD', ilvl=0, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml


class MangledIlvlTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA
        \end{enumerate}
        \begin{enumerate}
            \item BBB
                \begin{enumerate}
                    \item CCC
                \end{enumerate}
        \end{enumerate}
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 2),
            ('BBB', 1, 1),
            ('CCC', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class SeperateListsTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA
        \end{enumerate}
        \begin{enumerate}
            \item BBB
        \end{enumerate}
        \begin{enumerate}
            \item CCC
        \end{enumerate}
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 2),
            # Because AAA and CCC are part of the same list (same list id)
            # and BBB is different, these need to be split into three
            # lists (or lose everything from BBB and after.
            ('BBB', 0, 1),
            ('CCC', 0, 2),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)

        xml = DXB.xml(lis)
        return xml


class InvalidIlvlOrderTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA
                \begin{enumerate}
                    \item BBB
                        \begin{enumerate}
                            \item CCC
                        \end {enumerate}
                \end{enumerate}
            \end{enumerate}
    '''

    def get_xml(self):
        tags = [
            DXB.li(text='AAA', ilvl=1, numId=1),
            DXB.li(text='BBB', ilvl=3, numId=1),
            DXB.li(text='CCC', ilvl=2, numId=1),
        ]
        body = ''
        for el in tags:
            body += el

        xml = DXB.xml(body)
        return xml


class NonStandardTextTagsTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \added[id=, remark=]{insert} smarttag
    '''

    def get_xml(self):
        run_tags = [DXB.r_tag(i) for i in 'insert ']
        insert_tag = DXB.insert_tag(run_tags)
        run_tags = [DXB.r_tag(i) for i in 'smarttag']
        smart_tag = DXB.smart_tag(run_tags)

        run_tags = [insert_tag, smart_tag]
        body = DXB.p_tag(run_tags)
        xml = DXB.xml(body)
        return xml


class RTagWithNoText(_LatexTranslationTestCase):
    expected_output = ''

    def get_xml(self):
        p_tag = DXB.p_tag(None)  # No text
        run_tags = [p_tag]
        # The bug is only present in a hyperlink
        run_tags = [DXB.hyperlink_tag(r_id='rId0', run_tags=run_tags)]
        body = DXB.p_tag(run_tags)

        xml = DXB.xml(body)
        return xml


class DeleteTagInList(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA \\
                \deleted[id=, remark=]{BBB}
            \item CCC
        \end{enumerate}
    '''

    def get_xml(self):
        delete_tags = DXB.delete_tag(['BBB'])
        p_tag = DXB.p_tag([delete_tags])

        body = DXB.li(text='AAA', ilvl=0, numId=0)
        body += p_tag
        body += DXB.li(text='CCC', ilvl=0, numId=0)

        xml = DXB.xml(body)
        return xml


class InsertTagInList(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA \\
                \added[id=,remark=]{BBB}
            \item CCC
        \end{enumerate}
    '''

    def get_xml(self):
        run_tags = [DXB.r_tag(i) for i in 'BBB']
        insert_tags = DXB.insert_tag(run_tags)
        p_tag = DXB.p_tag([insert_tags])

        body = DXB.li(text='AAA', ilvl=0, numId=0)
        body += p_tag
        body += DXB.li(text='CCC', ilvl=0, numId=0)

        xml = DXB.xml(body)
        return xml


class SmartTagInList(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA \\
                BBB
            \item CCC
        \end{enumerate}
    '''

    def get_xml(self):
        run_tags = [DXB.r_tag(i) for i in 'BBB']
        smart_tag = DXB.smart_tag(run_tags)
        p_tag = DXB.p_tag([smart_tag])

        body = DXB.li(text='AAA', ilvl=0, numId=0)
        body += p_tag
        body += DXB.li(text='CCC', ilvl=0, numId=0)

        xml = DXB.xml(body)
        return xml


class SingleListItem(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
        \item AAA
        \end{enumerate}''' + '\n' + 'BBB'

    numbering_dict = {
        '1': {
            '0': 'lowerLetter',
        }
    }

    def get_xml(self):
        li = DXB.li(text='AAA', ilvl=0, numId=1)
        p_tags = [
            DXB.p_tag('BBB'),
        ]
        body = li
        for p_tag in p_tags:
            body += p_tag
        xml = DXB.xml(body)
        return xml


class SimpleTableTest(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{tabular} { lll }
                Blank &
                Column 1 &
                Column 2 \\
                Row 1 &
                First &
                Second \\
                Row 2 &
                Third &
                Fourth \\
        \end{tabular}'''

    def get_xml(self):
        table = DXB.table(num_rows=3, num_columns=3, text=chain(
            [DXB.p_tag('Blank')],
            [DXB.p_tag('Column 1')],
            [DXB.p_tag('Column 2')],
            [DXB.p_tag('Row 1')],
            [DXB.p_tag('First')],
            [DXB.p_tag('Second')],
            [DXB.p_tag('Row 2')],
            [DXB.p_tag('Third')],
            [DXB.p_tag('Fourth')],
        ), merge=True)
        body = table

        xml = DXB.xml(body)
        return xml


class MissingIlvl(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA \\
                BBB
            \item CCC
        \end{enumerate}
    '''

    def get_xml(self):
        li_text = [
            ('AAA', 0, 1),
            ('BBB', None, 1),  # Because why not.
            ('CCC', 0, 1),
        ]
        lis = ''
        for text, ilvl, numId in li_text:
            lis += DXB.li(text=text, ilvl=ilvl, numId=numId)
        body = lis
        xml = DXB.xml(body)
        return xml


class SDTTestCase(_LatexTranslationTestCase):
    expected_output = r'''
        \begin{enumerate}
            \item AAA \\
                BBB
            \item CCC
        \end{enumerate}
    '''

    def get_xml(self):
        body = ''
        body += DXB.li(text='AAA', ilvl=0, numId=0)
        body += DXB.sdt_tag(p_tag=DXB.p_tag(text='BBB'))
        body += DXB.li(text='CCC', ilvl=0, numId=0)

        xml = DXB.xml(body)
        return xml

#TODO: WORKOUT IMAGE CONVERSIONS
#TODO: IMAGE NOSIZE TESTCASE
