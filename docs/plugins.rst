#######
Plugins
#######

You may find yourself needing
a feature in PyDocX that doesn't exist
in the core library.

If it's something that should exist, the
PyDocX project is always open to new
contributions. Details of how to contibute
can be found in :doc:`/development`.

For things that don't fit in the core
library, it's easy to build a plugin
based on the :doc:`Extending PyDocX </extending>` and
:doc:`Export Mixins </export_mixins>` sections.

If you do build a plugin, edit this
documentation and add it below so that
other developers can find it.

-----------------
Available Plugins
-----------------

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Plugin
     - Description
   * - `pydocx-resize-images <https://github.com/jhubert/pydocx-resize-images>`_
     - Resizes large images to the dimensions they are in the docx file
   * - `pydocx-s3-images <https://github.com/jhubert/pydocx-s3-images>`_
     - Uploads images to S3 instead of returning Data URIs
