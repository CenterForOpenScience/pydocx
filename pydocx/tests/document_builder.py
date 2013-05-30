from jinja2 import Environment, PackageLoader
from pydocx.DocxParser import EMUS_PER_PIXEL

templates = {
    'delete': 'text_delete.xml',
    'drawing': 'drawing.xml',
    'hyperlink': 'hyperlink.xml',
    'insert': 'insert.xml',
    'linebreak': 'linebreak.xml',
    'main': 'base.xml',
    'p': 'p.xml',
    'pict': 'pict.xml',
    'r': 'r.xml',
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
        'pydocx.tests',
        'templates',
    ),
)


class DocxBuilder(object):

    @classmethod
    def xml(self, body):
        template = env.get_template(templates['main'])
        return template.render(body=body)

    @classmethod
    def p_tag(
            self,
            text,
            bold=False,
            underline=False,
            italics=False,
            style='style0',
            val=None,
            jc=None,
    ):
        if isinstance(text, str):
            # Use create a single r tag based on the text and the bold
            run_tag = DocxBuilder.r_tag(
                [DocxBuilder.t_tag(text)],
                is_bold=bold,
                is_underline=underline,
                is_italics=italics,
                val=val,
            )
            run_tags = [run_tag]
        elif isinstance(text, list):
            run_tags = text
        else:
            run_tags = [self.r_tag([])]
        template = env.get_template(templates['p'])

        kwargs = {
            'run_tags': run_tags,
            'style': style,
            'jc': jc,
        }
        return template.render(**kwargs)

    @classmethod
    def linebreak(self):
        template = env.get_template(templates['linebreak'])
        kwargs = {}
        return template.render(**kwargs)

    @classmethod
    def t_tag(self, text):
        template = env.get_template(templates['t'])
        kwargs = {
            'text': text,
        }
        return template.render(**kwargs)

    @classmethod
    def r_tag(
            self,
            elements,
            is_bold=False,
            is_underline=False,
            is_italics=False,
            val=None,
    ):
        template = env.get_template(templates['r'])
        kwargs = {
            'elements': elements,
            'is_bold': is_bold,
            'is_underline': is_underline,
            'is_italics': is_italics,
            'val': val,
        }
        return template.render(**kwargs)

    @classmethod
    def hyperlink_tag(self, r_id, run_tags):
        template = env.get_template(templates['hyperlink'])
        kwargs = {
            'r_id': r_id,
            'run_tags': run_tags,
        }
        return template.render(**kwargs)

    @classmethod
    def insert_tag(self, run_tags):
        template = env.get_template(templates['insert'])
        kwargs = {
            'run_tags': run_tags,
        }
        return template.render(**kwargs)

    @classmethod
    def delete_tag(self, deleted_texts):
        template = env.get_template(templates['delete'])
        kwargs = {
            'deleted_texts': deleted_texts,
        }
        return template.render(**kwargs)

    @classmethod
    def smart_tag(self, run_tags):
        template = env.get_template(templates['smartTag'])
        kwargs = {
            'run_tags': run_tags,
        }
        return template.render(**kwargs)

    @classmethod
    def sdt_tag(self, p_tag):
        template = env.get_template(templates['sdt'])
        kwargs = {
            'p_tag': p_tag,
        }
        return template.render(**kwargs)

    @classmethod
    def li(self, text, ilvl, numId, bold=False):
        if isinstance(text, str):
            # Use create a single r tag based on the text and the bold
            run_tag = DocxBuilder.r_tag([DocxBuilder.t_tag(text)], bold)
            run_tags = [run_tag]
        elif isinstance(text, list):
            run_tags = []
            for run_text, run_bold in text:
                run_tags.append(
                    DocxBuilder.r_tag(
                        [DocxBuilder.t_tag(run_tags)],
                        run_bold,
                    ),
                )
        else:
            raise AssertionError('text must be a string or a list')
        template = env.get_template(templates['p'])

        kwargs = {
            'run_tags': run_tags,
            'is_list': True,
            'ilvl': ilvl,
            'numId': numId,
        }
        return template.render(**kwargs)

    @classmethod
    def table(self, num_rows, num_columns, text, merge=False):

        def _tc(cell_value):
            template = env.get_template(templates['tc'])
            return template.render(p_tag=cell_value, merge=merge)

        def _tr(rows, text):
            tcs = [_tc(text.next()) for _ in range(rows)]
            template = env.get_template(templates['tr'])
            return template.render(table_cells=tcs)

        trs = [_tr(num_rows, text) for _ in range(num_rows)]
        template = env.get_template(templates['table'])
        return template.render(table_rows=trs)

    @classmethod
    def drawing(self, r_id, height=None, width=None):
        template = env.get_template(templates['drawing'])
        if height is not None:
            height = height * EMUS_PER_PIXEL
        if width is not None:
            width = width * EMUS_PER_PIXEL
        kwargs = {
            'r_id': r_id,
            'height': height,
            'width': width,
        }
        return template.render(**kwargs)

    @classmethod
    def pict(self, r_id=None, height=None, width=None):
        template = env.get_template(templates['pict'])
        kwargs = {
            'r_id': r_id,
            'height': height,
            'width': width,
        }
        return template.render(**kwargs)

    @classmethod
    def sectPr_tag(self, p_tag):
        template = env.get_template(templates['sectPr'])

        kwargs = {
            'p_tag': p_tag,
        }
        return template.render(**kwargs)

    @classmethod
    def styles_xml(self, style_tags):
        template = env.get_template(templates['styles'])

        kwargs = {
            'style_tags': style_tags,
        }
        return template.render(**kwargs)

    @classmethod
    def style(self, style_id, value):
        template = env.get_template(templates['style'])

        kwargs = {
            'style_id': style_id,
            'value': value,
        }

        return template.render(**kwargs)
