from jinja2 import Environment, PackageLoader
from pydocx.DocxParser import EMUS_PER_PIXEL

templates = {
    'drawing': 'drawing.xml',
    'hyperlink': 'hyperlink.xml',
    'insert': 'insert.xml',
    'main': 'base.xml',
    'p': 'p.xml',
    'pict': 'pict.xml',
    'r': 'r.xml',
    'sectPr': 'sectPr.xml',
    'smartTag': 'smart_tag.xml',
    'style': 'style.xml',
    'styles': 'styles.xml',
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
    def p_tag(self, text, bold=False, val=None):
        if isinstance(text, str):
            # Use create a single r tag based on the text and the bold
            run_tag = DocxBuilder.r_tag(text, bold, val)
            run_tags = [run_tag]
        elif isinstance(text, list):
            run_tags = text
        else:
            run_tags = [self.r_tag(None)]
        template = env.get_template(templates['p'])

        kwargs = {
            'run_tags': run_tags,
        }
        return template.render(**kwargs)

    @classmethod
    def r_tag(self, text, is_bold=False, val=None, include_linebreak=False):
        template = env.get_template(templates['r'])
        kwargs = {
            'text': text,
            'is_bold': is_bold,
            'val': val,
            'include_linebreak': include_linebreak,
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
    def smart_tag(self, run_tags):
        template = env.get_template(templates['smartTag'])
        kwargs = {
            'run_tags': run_tags,
        }
        return template.render(**kwargs)

    @classmethod
    def li(self, text, ilvl, numId, bold=False):
        if isinstance(text, str):
            # Use create a single r tag based on the text and the bold
            run_tag = DocxBuilder.r_tag(text, bold)
            run_tags = [run_tag]
        elif isinstance(text, list):
            run_tags = []
            for run_text, run_bold in text:
                run_tags.append(DocxBuilder.r_tag(run_tags, run_bold))
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
    def table(self, num_rows, num_columns, text):

        def _tc(cell_value):
            template = env.get_template(templates['tc'])
            return template.render(p_tag=cell_value)

        def _tr(rows, text):
            tcs = [_tc(text.next()) for _ in range(rows)]
            template = env.get_template(templates['tr'])
            return template.render(table_cells=tcs)

        trs = [_tr(num_rows, text) for _ in range(num_rows)]
        template = env.get_template(templates['table'])
        return template.render(table_rows=trs)

    @classmethod
    def drawing(self, height, width, r_id):
        template = env.get_template(templates['drawing'])
        kwargs = {
            'r_id': r_id,
            'height': height * EMUS_PER_PIXEL,
            'width': width * EMUS_PER_PIXEL,
        }
        return template.render(**kwargs)

    @classmethod
    def pict(self, height, width, r_id=None):
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
