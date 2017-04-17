# coding: utf-8
from __future__ import (
    absolute_import,
    division,
    print_function,
    unicode_literals,
)

from pydocx.export.image_resize import (
    ImageResizer,
    get_image_data_and_filename,
)


class ResizedImagesExportMixin(object):
    def image(self, image_data, filename, x, y, uri_is_external):

        if uri_is_external:
            image_data, filename = get_image_data_and_filename(
                image_data,
                filename,
            )

        image_resizer = ImageResizer(image_data, filename, x, y)

        if image_resizer.has_skippable_extension():
            return ''

        if not image_resizer.has_height_and_width():
            return ''

        image_resizer.init_image()
        image_resizer.resize_image()
        image_resizer.update_filename()

        return super(
            ResizedImagesExportMixin,
            self,
        ).image(
            image_resizer.image_data,
            image_resizer.filename,
            image_resizer.x,
            image_resizer.y,
            uri_is_external)
