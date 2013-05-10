#import mock
import tempfile
import shutil
from os import path
#from zipfile import ZipFile
from nose.plugins.skip import SkipTest
#from nose.tools import assert_raises

from pydocx.tests import assert_html_equal
from pydocx.parsers.Docx2Html import Docx2Html


class TestDocx2HTML(Docx2Html):
    def head(self):
        return ''

    def table(self, text):
        return '<table>' + text + '</table>'

    def ordered_list(self, text, list_style):
        list_type_conversions = {
            'decimal': 'decimal',
            'decimalZero': 'decimal-leading-zero',
            'upperRoman': 'upper-roman',
            'lowerRoman': 'lower-roman',
            'upperLetter': 'upper-alpha',
            'lowerLetter': 'lower-alpha',
            'ordinal': 'decimal',
            'cardinalText': 'decimal',
            'ordinalText': 'decimal',
        }
        return '<ol data-list-type="{list_style}">{text}</ol>'.format(
            list_style=list_type_conversions.get(list_style, 'decimal'),
            text=text,
        )


def convert(path):
    return TestDocx2HTML(path).parsed


def test_extract_html():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'simple.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <p>
          Simple text
        </p>
        <ol data-list-type="decimal">
          <li>one</li>
          <li>two</li>
          <li>three</li>
        </ol>
        <table>
          <tr>
            <td>Cell1</td>
            <td>Cell2</td>
          </tr>
          <tr>
            <td>Cell3</td>
            <td>cell4</td>
          </tr>
        </table>
    </body></html>
    ''')


def test_nested_list():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'nested_lists.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <ol data-list-type="decimal">
            <li>one</li>
            <li>two</li>
            <li>three
                <ol data-list-type="decimal">
                    <li>AAA</li>
                    <li>BBB</li>
                    <li>CCC
                        <ol data-list-type="decimal">
                            <li>alpha</li>
                        </ol>
                    </li>
                </ol>
            </li>
            <li>four</li>
        </ol>
        <ol data-list-type="decimal">
            <li>xxx
                <ol data-list-type="decimal">
                    <li>yyy</li>
                </ol>
            </li>
        </ol>
        <ul>
            <li>www
                <ul>
                    <li>zzz</li>
                </ul>
            </li>
        </ul>
    </body></html>
    ''')


def test_simple_list():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'simple_lists.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <ol data-list-type="decimal">
            <li>One</li>
        </ol>
        <ul>
            <li>two</li>
        </ul>
    </body></html>
    ''')


def test_inline_tags():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'inline_tags.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body><p>This sentence has some <b>bold</b>, some <i>italics</i> and some <u>underline</u>, as well as a <a href="http://www.google.com/">hyperlink</a>.</p></body></html>''')  # noqa


def test_unicode():
    raise SkipTest('This test is not yet passing')
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'greek_alphabet.docx',
    )
    actual_html = convert(file_path)
    assert actual_html is not None


def test_special_chars():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'special_chars.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body><p>&amp; &lt; &gt; <a href="https://www.google.com/?test=1&amp;more=2">link</a></p></body></html>''')  # noqa


def test_table_col_row_span():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'table_col_row_span.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
      <table>
        <tr>
          <td colspan="2">AAA</td>
        </tr>
        <tr>
          <td rowspan="2">BBB</td>
          <td>CCC</td>
        </tr>
        <tr>
          <td>DDD</td>
        </tr>
        <tr>
          <td>
          <div class='right'>EEE
          </div></td>
          <td rowspan="2">FFF</td>
        </tr>
        <tr>
          <td>
           <div class='right'>GGG
           </div></td>
        </tr>
      </table>
      <table>
        <tr>
          <td>1</td>
          <td>2</td>
          <td>3</td>
          <td>4</td>
        </tr>
        <tr>
          <td>5</td>
          <td colspan="2" rowspan="2">6</td>
          <td>7</td>
        </tr>
        <tr>
          <td>8</td>
          <td>9</td>
        </tr>
        <tr>
          <td>10</td>
          <td>11</td>
          <td>12</td>
          <td>13</td>
        </tr>
      </table>
    </body></html>
    ''')


def test_nested_table_rowspan():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'nested_table_rowspan.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <table>
            <tr>
                <td colspan="2">AAA</td>
            </tr>
            <tr>
                <td>BBB</td>
                <td>
                    <table>
                        <tr>
                            <td rowspan="2">CCC</td>
                            <td>DDD</td>
                        </tr>
                        <tr>
                            <td>EEE</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body></html>
    ''')


def test_nested_tables():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'nested_tables.docx',
    )
    actual_html = convert(file_path)
    # Find out why br tag is there.
    assert_html_equal(actual_html, '''
    <html><body>
        <table>
            <tr>
                <td>AAA</td>
                <td>BBB</td>
            </tr>
            <tr>
                <td>CCC</td>
                <td>
                    <table>
                        <tr>
                            <td>DDD</td>
                            <td>EEE</td>
                        </tr>
                        <tr>
                            <td>FFF</td>
                            <td>GGG</td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body></html>
    ''')


def test_list_in_table():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'list_in_table.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <table>
          <tr>
            <td>
              <ol data-list-type="decimal">
                <li>AAA</li>
                <li>BBB</li>
                <li>CCC</li>
              </ol>
            </td>
          </tr>
        </table>
    </body></html>
    ''')


def test_tables_in_lists():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'tables_in_lists.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <ol data-list-type="decimal">
            <li>AAA</li>
            <li>BBB
                <table>
                    <tr>
                        <td>CCC</td>
                        <td>DDD</td>
                    </tr>
                    <tr>
                        <td>EEE</td>
                        <td>FFF</td>
                    </tr>
                </table>
            </li>
            <li>GGG</li>
        </ol>
    </body></html>
    ''')


def test_track_changes_on():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'track_changes_on.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body><p>This was some content.</p></body></html>
    ''')


def test_headers():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'headers.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <h1>This is an H1</h1>
        <h2>This is an H2</h2>
        <h3>This is an H3</h3>
        <h4>This is an H4</h4>
        <h5>This is an H5</h5>
        <h6>This is an H6</h6>
        <h6>This is an H7</h6>
        <h6>This is an H8</h6>
        <h6>This is an H9</h6>
        <h6>This is an H10</h6>
    </body></html>
    ''')


def _copy_file_to_tmp_dir(file_path, filename):
    # Since the images need to be extracted from the docx, copy the file to a
    # temp directory so we do not clutter up repo.
    dp = tempfile.mkdtemp()
    new_file_path = path.join(dp, filename)
    shutil.copyfile(file_path, new_file_path)
    return new_file_path, dp


def test_split_headers():
    filename = 'split_header.docx'
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'split_header.docx',
    )
    # preserve_images must be true in order for the image to not be removed.
    # This is handled in build_import, however here we need to manually set it
    # to True.
    new_file_path, _ = _copy_file_to_tmp_dir(file_path, filename)

    actual_html = convert(new_file_path)
    assert_html_equal(actual_html, '''
    <html><body><h1>AAA</h1><p>BBB</p><h1>CCC</h1></body></html>
    ''')


def test_has_image():
    filename = 'has_image.docx'
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'has_image.docx',
    )
    # preserve_images must be true in order for the image to not be removed.
    # This is handled in build_import, however here we need to manually set it
    # to True.
    new_file_path, dp = _copy_file_to_tmp_dir(file_path, filename)

    actual_html = convert(new_file_path)
    # Ignore height, width for now.
    assert_html_equal(actual_html, '''
    <html><body>
        <p>AAA<img src="media/image1.gif" height="55px" width="260px" /></p>
    </body></html>
    ''')


def test_has_image_using_image_handler():
    raise SkipTest('This needs to be converted to an xml test')
    filename = 'has_image.docx'
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'has_image.docx',
    )
    # preserve_images must be true in order for the image to not be removed.
    # This is handled in build_import, however here we need to manually set it
    # to True.
    new_file_path, _ = _copy_file_to_tmp_dir(file_path, filename)

    def image_handler(*args, **kwargs):
        return 'test'
    actual_html = convert(new_file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <p>AAA<img src="test" height="55" width="260" /></p>
    </body></html>
    ''')


#def test_attachment_is_tiff():
#    filename = 'attachment_is_tiff.docx'
#    file_path = path.join(
#        path.abspath(path.dirname(__file__)),
#        '..',
#        'fixtures',
#        'attachment_is_tiff.docx',
#    )
#    # preserve_images must be true in order for the image to not be removed.
#    # This is handled in build_import, however here we need to manually set it
#    # to True.
#    new_file_path, _ = _copy_file_to_tmp_dir(file_path, filename)
#
#    # First open the file and verify that the image attachment is a tiff.
#    try:
#        zf = ZipFile(new_file_path)
#        # Get the document data.
#        _, meta_data = _get_document_data(zf)
#    finally:
#        zf.close()
#    # Find the path to the image.
#    image_file = None
#    for file_path in meta_data.relationship_dict.values():
#        if file_path.endswith('.gif'):
#            image_file = file_path
#    assert image_file is not None
#    with open(image_file) as f:
#        magic_number = f.read()[:4]
#    # Make sure the image is actually a gif.
#    assert magic_number == 'GIF8'


def test_headers_with_full_line_styles():
    raise SkipTest('This test is not yet passing')
    # Show that if a natural header is completely bold/italics that
    # bold/italics will get stripped out.
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'headers_with_full_line_styles.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <h2>AAA</h2>
        <h2>BBB</h2>
        <h2><strong>C</strong><em>C</em>C</h2>
    </body></html>
    ''')


def test_convert_p_to_h():
    raise SkipTest('This test is not yet passing')
    # Show when it is correct to convert a p tag to an h tag based on
    # bold/italics
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'convert_p_to_h.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <h2>AAA</h2>
        <h2>BBB</h2>
        <p>CCC</p>
        <ol data-list-type="decimal">
            <li><strong>DDD</strong></li>
            <li><em>EEE</em></li>
            <li>FFF</li>
        </ol>
        <table>
            <tr>
                <td><strong>GGG</strong></td>
                <td><em>HHH</em></td>
            </tr>
            <tr>
                <td>III</td>
                <td>JJJ</td>
            </tr>
        </table>
    </body></html>
    ''')


#def test_bigger_font_size_to_header():
#    # Show when it is appropriate to convert p tags to h tags based on font
#    # size.
#    if not DETECT_FONT_SIZE:
#        raise SkipTest('Font size detection is disabled.')
#    file_path = path.join(
#        path.abspath(path.dirname(__file__)),
#        '..',
#        'fixtures',
#        'bigger_font_size_to_header.docx',
#    )
#    actual_html = convert(file_path)
#    assert_html_equal(actual_html, '''
#    <html>
#        <p>Paragraphs:</p>
#        <h2>Header</h2>
#        <p>paragraph 1</p>
#        <p>Lists:</p>
#        <ol data-list-type="decimal">
#            <li>bigger</li>
#            <li>smaller</li>
#        </ol>
#        <p>Tables:</p>
#        <table>
#            <tr>
#                <td>bigger</td>
#                <td>smaller</td>
#            </tr>
#        </table>
#    </html>
#    ''')


def test_fake_headings_by_length():
    raise SkipTest('This test is not yet passing')
    # Show that converting p tags to h tags has a length limit. If the p tag is
    # supposed to be converted to an h tag but has more than seven words in the
    # paragraph do not convert it.
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'fake_headings_by_length.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <h2>Heading.</h2>
        <h2>Still a heading.</h2>
        <p>
        <strong>This is not a heading because it is too many words.</strong>
        </p>
    </body></html>
    ''')


def test_shift_enter():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'shift_enter.docx',
    )

    # Test just the convert without clean_html to make sure the first
    # break tag is present.
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <p>AAA<br/>BBB</p>
        <p>CCC</p>
        <ol data-list-type="decimal">
            <li>DDD<br/>EEE</li>
            <li>FFF</li>
        </ol>
        <table>
            <tr>
                <td>GGG<br/>HHH</td>
                <td>III<br/>JJJ</td>
            </tr>
            <tr>
                <td>KKK</td>
                <td>LLL</td>
            </tr>
        </table>
    </body></html>
    ''')


def test_lists_with_styles():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'lists_with_styles.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <ol data-list-type="decimal">
            <li>AAA</li>
            <li>BBB
                <ol data-list-type="lower-roman">
                    <li>CCC</li>
                    <li>DDD
                        <ol data-list-type="upper-alpha">
                            <li>EEE
                                <ol data-list-type="lower-alpha">
                                    <li>FFF</li>
                                </ol>
                            </li>
                        </ol>
                    </li>
                </ol>
            </li>
        </ol>
    </body></html>
    ''')


def test_list_to_header():
    raise SkipTest('This test is not yet passing')
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'list_to_header.docx',
    )
    actual_html = convert(file_path)
    # It should be noted that list item `GGG` is upper roman in the word
    # document to show that only top level upper romans get converted.
    assert_html_equal(actual_html, '''
    <html><body>
        <h2>AAA</h2>
        <ol data-list-type="decimal">
            <li>BBB</li>
        </ol>
        <h2>CCC</h2>
        <ol data-list-type="decimal">
            <li>DDD</li>
        </ol>
        <h2>EEE</h2>
        <ol data-list-type="decimal">
            <li>FFF
                <ol data-list-type="upper-roman">
                    <li>GGG</li>
                </ol>
            </li>
        </ol>
    </body></html>
    ''')


def test_has_title():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'has_title.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(
        actual_html,
        '''<html><body><p>Title</p>
        <p><div class='left'>Text</div></p></body></html>''',
    )


def test_upper_alpha_all_bold():
    raise SkipTest('This test is not yet passing')
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'upper_alpha_all_bold.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
    <html><body>
        <h2>AAA</h2>
        <h2>BBB</h2>
        <h2>CCC</h2>
    </body></html>
    ''')


def test_justification():
    file_path = path.join(
        path.abspath(path.dirname(__file__)),
        '..',
        'fixtures',
        'justification.docx',
    )
    actual_html = convert(file_path)
    assert_html_equal(actual_html, '''
<html><body><p><div class='center'>Center Justified</div>
</p><p><div class='right'>Right justified</div></p>
<p><div class='right' style ='margin-right:96.0px;'>
Right justified and pushed in from right</div></p>
<p><div class='center' style ='margin-left:252.0px;'margin-right:96.0px;'>
Center justified and pushed in from left and it is
great and it is the coolest thing of all time and I like it and
I think it is cool</div></p><p>
<div' style ='margin-left:252.0px;'margin-right:96.0px;'>
Left justified and pushed in from left</div></p></body></html>
''')


def _converter(*args, **kwargs):
    # Having a converter that does nothing is the same as if abiword fails to
    # convert.
    pass


#def test_converter_broken():
#    file_path = 'test.doc'
#    assert_raises(
#        ConversionFailed,
#        lambda: convert(file_path, converter=_converter),
#    )


def test_fall_back():
    raise SkipTest('This test is not yet passing')
    file_path = 'test.doc'

    def fall_back(*args, **kwargs):
        return 'success'
    html = convert(file_path, fall_back=fall_back, converter=_converter)
    assert html == 'success'


#@mock.patch('docx2html.core.read_html_file')
#@mock.patch('docx2html.core.get_zip_file_handler')
#def test_html_files(patch_zip_handler, patch_read):
def test_html_files():
    raise SkipTest('This test is not yet passing')

    def raise_assertion(*args, **kwargs):
        raise AssertionError('Should not have called get_zip_file_handler')
    #patch_zip_handler.side_effect = raise_assertion

    def return_text(*args, **kwargs):
        return 'test'
    #patch_read.side_effect = return_text

    # Try with an html file
    file_path = 'test.html'

    html = convert(file_path)
    assert html == 'test'

    # Try again with an htm file.
    file_path = 'test.htm'

    html = convert(file_path)
    assert html == 'test'
