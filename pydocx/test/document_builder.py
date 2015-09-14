from __future__ import (
    absolute_import,
    print_function,
    unicode_literals,
)


from jinja2 import Environment, PackageLoader
from pydocx.constants import EMUS_PER_PIXEL

templates = {
    'delete': 'text_delete.xml',
    'drawing': 'drawing.xml',
    'hyperlink': 'hyperlink.xml',
    'insert': 'insert.xml',
    'linebreak': 'linebreak.xml',
    'main': 'base.xml',
    'numbering': 'numbering.xml',
    'p': 'p.xml',
    'pict': 'pict.xml',
    'r': 'r.xml',
    'rpr': 'rpr.xml',
    'sdt': 'sdt.xml',
    'sectPr': 'sectPr.xml',
    'smartTag': 'smart_tag.xml',
    'style': 'style.xml',
    'styles': 'styles.xml',
    't': 't.xml',
    'table': 'table.xml',
    'tc': 'tc.xml',
    'tr': 'tr.xml',
}

env = Environment(
    loader=PackageLoader(
        'tests',
        'templates',
    ),
)

try:
    string_types = (str, unicode)
except NameError:
    string_types = str


def template_render(template, **render_args):
    '''
    Return a utf-8 bytestream of the rendered template
    '''
    return template.render(**render_args).encode('utf-8')


class DocxBuilder(object):

    @classmethod
    def xml(self, body):
        template = env.get_template(templates['main'])
        return template_render(
            template,
            body=body.decode('utf-8'),
        )

    @classmethod
    def p_tag(
            self,
            text,
            style='style0',
            jc=None,
    ):
        if isinstance(text, string_types):
            # Use create a single r tag based on the text and the bold
            run_tag = DocxBuilder.r_tag(
                [DocxBuilder.t_tag(text)],
            )
            run_tags = [run_tag]
        elif isinstance(text, list):
            run_tags = text
        else:
            run_tags = [self.r_tag([])]
        template = env.get_template(templates['p'])

        return template_render(
            template,
            run_tags=run_tags,
            style=style,
            jc=jc,
        )

    @classmethod
    def linebreak(self):
        template = env.get_template(templates['linebreak'])
        return template_render(template)

    @classmethod
    def t_tag(self, text):
        template = env.get_template(templates['t'])
        return template_render(template, text=text)

    @classmethod
    def r_tag(
            self,
            elements,
            rpr=None,
    ):
        template = env.get_template(templates['r'])
        if rpr is None:
            rpr = DocxBuilder.rpr_tag()
        return template_render(
            template,
            elements=elements,
            rpr=rpr,
        )

    @classmethod
    def rpr_tag(self, inline_styles=None, *args, **kwargs):
        if inline_styles is None:
            inline_styles = {}
        valid_styles = (
            'b',
            'i',
            'u',
            'caps',
            'smallCaps',
            'strike',
            'dstrike',
            'vanish',
            'webHidden',
            'vertAlign',
        )
        for key in inline_styles:
            if key not in valid_styles:
                raise AssertionError('%s is not a valid style' % key)
        template = env.get_template(templates['rpr'])
        return template_render(
            template,
            tags=inline_styles,
        )

    @classmethod
    def hyperlink_tag(self, r_id, run_tags):
        template = env.get_template(templates['hyperlink'])
        return template_render(
            template,
            r_id=r_id,
            run_tags=run_tags,
        )

    @classmethod
    def insert_tag(self, run_tags):
        template = env.get_template(templates['insert'])
        return template_render(
            template,
            run_tags=run_tags,
        )

    @classmethod
    def delete_tag(self, deleted_texts):
        template = env.get_template(templates['delete'])
        return template_render(
            template,
            deleted_texts=deleted_texts,
        )

    @classmethod
    def smart_tag(self, run_tags):
        template = env.get_template(templates['smartTag'])
        return template_render(
            template,
            run_tags=run_tags,
        )

    @classmethod
    def sdt_tag(self, p_tag):
        template = env.get_template(templates['sdt'])
        return template_render(
            template,
            p_tag=p_tag,
        )

    @classmethod
    def li(self, text, ilvl, numId, bold=False):
        if isinstance(text, list):
            run_tags = []
            for run_text, run_bold in text:
                run_tags.append(
                    DocxBuilder.r_tag(
                        [DocxBuilder.t_tag(run_tags)],
                        run_bold,
                    ),
                )
        else:
            # Assume a string type
            # Use create a single r tag based on the text and the bold
            run_tag = DocxBuilder.r_tag([DocxBuilder.t_tag(text)], bold)
            run_tags = [run_tag]
        template = env.get_template(templates['p'])

        return template_render(
            template,
            run_tags=run_tags,
            is_list=True,
            ilvl=ilvl,
            numId=numId,
        )

    @classmethod
    def table_cell(self, paragraph, merge=False, merge_continue=False):
        template = env.get_template(templates['tc'])
        return template_render(
            template,
            paragraph=paragraph,
            merge=merge,
            merge_continue=merge_continue,
        )

    @classmethod
    def table_row(self, tcs):
        template = env.get_template(templates['tr'])
        return template_render(
            template,
            table_cells=tcs,
        )

    @classmethod
    def table(self, trs):
        template = env.get_template(templates['table'])
        return template_render(
            template,
            table_rows=trs,
        )

    @classmethod
    def drawing(self, r_id, height=None, width=None):
        template = env.get_template(templates['drawing'])
        if height is not None:
            height = height * EMUS_PER_PIXEL
        if width is not None:
            width = width * EMUS_PER_PIXEL
        return template_render(
            template,
            r_id=r_id,
            height=height,
            width=width,
        )

    @classmethod
    def pict(self, r_id=None, height=None, width=None):
        template = env.get_template(templates['pict'])
        return template_render(
            template,
            r_id=r_id,
            height=height,
            width=width,
        )

    @classmethod
    def sectPr_tag(self, p_tag):
        template = env.get_template(templates['sectPr'])
        return template_render(
            template,
            p_tag=p_tag,
        )

    @classmethod
    def styles_xml(self, style_tags):
        template = env.get_template(templates['styles'])
        return template_render(
            template,
            style_tags=style_tags,
        )

    @classmethod
    def style(self, style_id, value):
        template = env.get_template(templates['style'])
        return template_render(
            template,
            style_id=style_id,
            value=value,
        )

    @classmethod
    def numbering(self, numbering_dict):
        template = env.get_template(templates['numbering'])
        return template_render(
            template,
            numbering_dict=numbering_dict,
        )
